#!/usr/bin/env node
/**
 * Book Machine Local Server  v1.0
 *
 * Bridges book-machine-local.html to:
 *   • Claude API (streaming, uses real skill files from skills/ folder)
 *   • Local filesystem (reads manuscripts, writes files — no dialog prompts)
 *
 * Usage:  node book-machine-server.js
 *   (or double-click start-server.bat / start-server.sh)
 *
 * Requires ANTHROPIC_API_KEY environment variable (set it in your shell
 * profile or let the start script prompt you for it).
 */

const http  = require('http');
const https = require('https');
const fs    = require('fs');
const path  = require('path');

const PORT    = 7842;
const ROOT    = path.resolve(__dirname, '..');   // Book Machine root folder
const BOOKS   = path.join(ROOT, 'books');
const SKILLS  = path.join(ROOT, 'skills');

// ── Anthropic client (lazy — allows server to start without key) ──────────
let _client = null;
function getClient() {
  if (_client) return _client;
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error(
    'ANTHROPIC_API_KEY is not set.\n' +
    'Add it to your environment or let the start script prompt you.'
  );
  const { default: Anthropic } = require('@anthropic-ai/sdk');
  _client = new Anthropic({ apiKey: key });
  return _client;
}

// ── File helpers ──────────────────────────────────────────────────────────
function safeRead(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); } catch { return null; }
}
function wordCount(text) { return (text || '').split(/\s+/).filter(Boolean).length; }
function bookPath(bookFolder, ...parts) {
  return path.join(BOOKS, bookFolder, ...parts);
}
function assertSafe(abs) {
  if (!abs.startsWith(ROOT)) throw new Error('Path traversal blocked.');
}
function folderToTitle(s) {
  return s.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');
}

// ── Skill loader — reads actual .md skill files from skills/ folder ───────
function loadSkillPrompt(skillId) {
  const candidates = [
    path.join(SKILLS, 'race',        skillId, 'prompt.md'),
    path.join(SKILLS, 'race',        skillId + '.md'),
    path.join(SKILLS, 'parc-ferme',  skillId, 'prompt.md'),
    path.join(SKILLS, 'parc-ferme',  skillId + '.md'),
    path.join(SKILLS, 'garage',      skillId, 'prompt.md'),
    path.join(SKILLS, 'garage',      skillId + '.md'),
    path.join(SKILLS,                skillId + '.md'),
    path.join(SKILLS,                skillId, 'prompt.md'),
  ];
  for (const c of candidates) {
    const txt = safeRead(c);
    if (txt) { console.log(`  Skill loaded: ${c}`); return txt; }
  }
  return null;
}

// ── Book scanner (server-side, no File System Access API needed) ──────────
function scanBooks() {
  let entries;
  try { entries = fs.readdirSync(BOOKS); } catch { return []; }

  const books = [];
  for (const name of entries) {
    const dir = path.join(BOOKS, name);
    try { if (!fs.statSync(dir).isDirectory()) continue; } catch { continue; }

    const book = { folderName: name, title: folderToTitle(name), fromScan: true,
                   status: 'idle', wordsCurrent: 0, wordsTarget: 80000,
                   genre: '', series: '', logline: '', next: '', lastTouched: '' };

    const bo = safeRead(path.join(dir, 'book-order.md'));
    if (bo) {
      const m1 = bo.match(/^#\s+(?:Book Order\s*[-–—]\s*)?(.+)/im);
      if (m1) book.title = m1[1].trim();
      const m2 = bo.match(/\*\*Genre:\*\*\s*(.+)/i);
      if (m2) book.genre = m2[1].trim();
      const m3 = bo.match(/\*\*Target word count:\*\*\s*([\d,]+)/i);
      if (m3) book.wordsTarget = parseInt(m3[1].replace(/,/g,''));
      const m4 = bo.match(/\*\*Series or standalone:\*\*\s*(.+)/i);
      if (m4) book.series = m4[1].split('.')[0].trim();
      const m5 = bo.match(/\*\*Core question[^*]*\*\*\s*(.+)/i);
      if (m5 && !book.logline) book.logline = m5[1].trim();
    }

    const cleanMs = safeRead(path.join(dir, 'drafts', '_FULL_MANUSCRIPT_CLEAN.md'))
                 || safeRead(path.join(dir, 'drafts', '_FULL_MANUSCRIPT.md'));
    if (cleanMs) book.wordsCurrent = wordCount(cleanMs);

    const sr = safeRead(path.join(dir, 'SESSION_REPORT.md'));
    if (sr) {
      const d1 = sr.match(/\*\*Date:\*\*\s*(.+)/i); if (d1) book.lastTouched = d1[1].trim();
      const w1 = sr.match(/\*\*Manuscript length:\*\*\s*([\d,]+)/i);
      if (w1) book.wordsCurrent = parseInt(w1[1].replace(/,/g,''));
      if (/open items for revision/i.test(sr) || /parc.ferm[eé].*complete/i.test(sr)) book.status='revision';
      else if (/parc.ferm[eé]/i.test(sr)) book.status='editing';
      else if (/driver loop|laps drafted/i.test(sr)) book.status='drafting';
      const openM = sr.match(/##\s*Open Items[^\n]*\n([\s\S]+?)(?=\n##|\n---|\Z)/i);
      if (openM) {
        const items=[];
        for (const line of openM[1].split('\n')) {
          const m = line.match(/^\d+\.\s+\*\*(.+?)\*\*/);
          if (m) items.push(m[1]);
          if (items.length>=3) break;
        }
        if (items.length) book.next = items.join(' · ');
      }
    }

    // Skip obvious template placeholders
    if (book.title.includes('[') || book.title.includes('{')) continue;

    books.push(book);
  }
  return books;
}

// ── Prompt builder — reads real manuscript + skill prompt ─────────────────
function buildPrompt(body) {
  const { skill, storyFolder, filePath, customPrompt, authorName, extraContext } = body;

  if (skill === 'custom' && customPrompt) {
    return customPrompt;
  }

  const who = authorName ? `Author: ${authorName}.\n` : '';

  // Read skill prompt from files
  const skillText = loadSkillPrompt(skill);

  // Read manuscript / target file
  let fileContent = null;
  if (storyFolder && filePath) {
    const abs = path.resolve(bookPath(storyFolder, filePath));
    assertSafe(abs);
    fileContent = safeRead(abs);
  } else if (storyFolder) {
    fileContent = safeRead(bookPath(storyFolder, 'drafts', '_FULL_MANUSCRIPT_CLEAN.md'))
               || safeRead(bookPath(storyFolder, 'drafts', '_FULL_MANUSCRIPT.md'));
  }

  // Read story dossier for context
  let dossier = null;
  if (storyFolder) {
    dossier = safeRead(bookPath(storyFolder, 'state', 'story-dossier.md'))
           || safeRead(bookPath(storyFolder, 'state', 'manuscript-bible.md'))
           || safeRead(path.join(ROOT, 'Book machine', 'Story_Dossier_Worksheet.md'));
    if (dossier && dossier.length > 4000) dossier = dossier.slice(0, 4000) + '\n\n[…dossier truncated…]';
  }

  // Read CLAUDE.md rules if present
  const rules = safeRead(path.join(ROOT, 'Book machine', 'CLAUDE.md'))
             || safeRead(path.join(ROOT, 'CLAUDE.md'));

  const rulesBlock   = rules    ? `\n\n---\n\n## Project Rules\n\n${rules.slice(0,2000)}` : '';
  const dossierBlock = dossier  ? `\n\n---\n\n## Story Dossier\n\n${dossier}` : '';
  const fileBlock    = fileContent ? `\n\n---\n\n## Text to work on\n\n${fileContent}` : '';
  const extraBlock   = extraContext ? `\n\n---\n\n## Additional context\n\n${extraContext}` : '';

  if (skillText) {
    return `${who}${skillText}${rulesBlock}${dossierBlock}${fileBlock}${extraBlock}`;
  }

  // Built-in fallback prompts
  const fallbacks = {
    'driver':          `${who}You are the Driver — a skilled scene-level fiction writer. Continue drafting from where we left off. Write the next scene, maintaining voice and continuity. Aim for at least 1,500 words.`,
    'line-editor':     `${who}You are a professional line editor. Improve the text at the sentence level: show don't tell, active voice, rhythm, word choice, filter words, tight dialogue. Return the full improved text with brief notes.`,
    'dialogue-polish': `${who}Polish the dialogue. Each character should sound distinct, subtext should land, nothing on-the-nose. Return the improved text.`,
    'crutch-inspector':`${who}You are the Crutch Inspector. List overused words with counts, then the 5 worst with examples and rewrites.`,
    'proofreader':     `${who}Proofread: fix typos, grammar, punctuation, inconsistencies. Return corrected text with a change summary.`,
    'dev-editor':      `${who}Developmental editor: analyze structure, pacing, character arc, promise/payoff, POV. Write a structured diagnostic report. Diagnose, don't rewrite.`,
    'brainstorm':      `${who}Genre fiction brainstorm partner. Ask me one focused question to start developing a story concept — subgenre, vibe, tropes — then help build a premise and reader promise.`,
    'voice-self-edit': `${who}Voice consistency editor: identify and fix places where the narrative voice drifts from the established style. Return the improved text with notes on what shifted.`,
    'ai-decontam':     `${who}AI decontamination pass: find and remove AI-generated prose patterns (AI-isms), filler phrases, over-explained emotions, unearned epiphanies. Return the humanized text.`,
  };
  return (fallbacks[skill] || `${who}Help with the following task: ${skill}.`) + dossierBlock + fileBlock;
}

// ── OpenRouter streaming (built-in https — no extra package needed) ───────
function callOpenRouterStream(prompt, apiKey, model, sseRes) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model,
      stream:     true,
      max_tokens: 8192,
      messages:   [{ role: 'user', content: prompt }],
    });
    const options = {
      hostname: 'openrouter.ai',
      port:     443,
      path:     '/api/v1/chat/completions',
      method:   'POST',
      headers: {
        'Content-Type':   'application/json',
        'Authorization':  `Bearer ${apiKey}`,
        'HTTP-Referer':   'https://bookmachine.local',
        'X-Title':        'Book Machine Dashboard',
        'Content-Length': Buffer.byteLength(body),
      },
    };
    const req = https.request(options, apiRes => {
      let buf = '';
      apiRes.on('data', chunk => {
        buf += chunk.toString();
        const lines = buf.split('\n');
        buf = lines.pop();
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const d = line.slice(6).trim();
          if (d === '[DONE]') return;
          try {
            const text = JSON.parse(d).choices?.[0]?.delta?.content;
            if (text) sseRes.write(`data: ${JSON.stringify({ text })}\n\n`);
          } catch {}
        }
      });
      apiRes.on('end', resolve);
      apiRes.on('error', reject);
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ── HTTP handlers ─────────────────────────────────────────────────────────

function handleStatus(res) {
  const books = scanBooks();
  json(res, {
    ok:               true,
    version:          '1.0',
    root:             ROOT,
    port:             PORT,
    books:            books.map(b => ({ folderName: b.folderName, title: b.title, status: b.status })),
    hasApiKey:        !!process.env.ANTHROPIC_API_KEY,
    hasOpenRouterKey: !!process.env.OPENROUTER_API_KEY,
    skillDirs:        ['race','parc-ferme','garage'].filter(d => {
      try { return fs.statSync(path.join(SKILLS,d)).isDirectory(); } catch { return false; }
    }),
  });
}

function handleScan(res) {
  json(res, { books: scanBooks() });
}

function handleRead(url, res) {
  const book     = url.searchParams.get('book');
  const filePath = url.searchParams.get('path');
  if (!book || !filePath) return jsonError(res, 'Missing book or path param');
  const abs = path.resolve(bookPath(book, filePath));
  try { assertSafe(abs); } catch(e) { return jsonError(res, e.message); }
  const content = safeRead(abs);
  if (content === null) return jsonError(res, `File not found: ${filePath}`);
  json(res, { content, wordCount: wordCount(content), filePath });
}

function handleWrite(body, res) {
  const { bookFolder, filePath, content } = body;
  if (!bookFolder || !filePath || content == null) {
    return jsonError(res, 'Missing bookFolder, filePath, or content');
  }
  const abs = path.resolve(bookPath(bookFolder, filePath));
  try { assertSafe(abs); } catch(e) { return jsonError(res, e.message); }

  const before   = safeRead(abs);
  const wcBefore = wordCount(before);
  const wcAfter  = wordCount(content);

  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, content, 'utf8');

  console.log(`  ✓ Wrote: ${path.relative(ROOT, abs)} (${wcAfter} words, ${wcAfter>=wcBefore?'+':''}${wcAfter-wcBefore})`);
  json(res, { ok: true, filePath, wordCount: wcAfter, wordCountBefore: wcBefore, delta: wcAfter - wcBefore });
}

async function handleRun(body, res) {
  // Stream SSE response
  res.writeHead(200, {
    'Content-Type':  'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection':    'keep-alive',
  });

  let prompt;
  try {
    prompt = buildPrompt(body);
  } catch(e) {
    res.write(`data: ${JSON.stringify({ error: e.message })}\n\n`);
    return res.end();
  }

  // ── Decide: OpenRouter or Claude? ────────────────────────
  // OpenRouter key: request body takes priority, then env var
  const orKey   = body.openrouterKey   || process.env.OPENROUTER_API_KEY || '';
  const orModel = body.openrouterModel || body.model || '';
  // Use OpenRouter if: caller flagged it, OR model looks like "provider/model-name"
  const useOR   = body.useOpenRouter || (orModel.includes('/') && !!orKey);

  const model = useOR ? orModel : (body.model || 'claude-sonnet-4-6');
  console.log(`  ▶ Running: ${body.skill || 'custom'} | ${body.storyFolder || 'no story'} | ${useOR ? 'OpenRouter:' : ''}${model}`);

  try {
    if (useOR) {
      if (!orKey) throw new Error('No OpenRouter key. Add OPENROUTER_API_KEY env var or pass it from Settings.');
      await callOpenRouterStream(prompt, orKey, orModel, res);
      res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
    } else {
      const client = getClient();
      const stream = client.messages.stream({
        model,
        max_tokens: 8192,
        messages:   [{ role: 'user', content: prompt }],
      });
      for await (const chunk of stream) {
        if (chunk.type === 'content_block_delta' && chunk.delta?.text) {
          res.write(`data: ${JSON.stringify({ text: chunk.delta.text })}\n\n`);
        }
      }
      const usage = (await stream.finalMessage()).usage;
      res.write(`data: ${JSON.stringify({ done: true, usage })}\n\n`);
    }
  } catch(e) {
    console.error('  ✗ Run error:', e.message);
    res.write(`data: ${JSON.stringify({ error: e.message })}\n\n`);
  }
  res.end();
}

// ── HTTP server ───────────────────────────────────────────────────────────
async function readBody(req) {
  return new Promise(resolve => {
    let data = '';
    req.on('data', chunk => data += chunk);
    req.on('end', () => { try { resolve(JSON.parse(data || '{}')); } catch { resolve({}); } });
  });
}
function json(res, data, status = 200) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}
function jsonError(res, msg, status = 400) { json(res, { ok: false, error: msg }, status); }

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin',  '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }

  const url  = new URL(req.url, `http://localhost:${PORT}`);
  const body = req.method === 'POST' ? await readBody(req) : {};

  try {
    if (url.pathname === '/api/status') return handleStatus(res);
    if (url.pathname === '/api/scan')   return handleScan(res);
    if (url.pathname === '/api/read')   return handleRead(url, res);
    if (url.pathname === '/api/write')  return await handleWrite(body, res);
    if (url.pathname === '/api/run')    return await handleRun(body, res);
    json(res, { error: 'Not found' }, 404);
  } catch(e) {
    console.error('Handler error:', e);
    try { json(res, { error: e.message }, 500); } catch {}
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('\n  ╔══════════════════════════════════════╗');
  console.log('  ║      📚 Book Machine Server  v1.0    ║');
  console.log('  ╚══════════════════════════════════════╝');
  console.log(`\n  Listening:  http://localhost:${PORT}`);
  console.log(`  Root:       ${ROOT}`);
  console.log(`  Claude key: ${process.env.ANTHROPIC_API_KEY  ? '✓ set' : '✗ NOT SET — Claude agents will fail'}`);
  console.log(`  OR key:     ${process.env.OPENROUTER_API_KEY ? '✓ set' : '— not set (optional, pass from dashboard Settings)'}`);

  const books = scanBooks();
  if (books.length) {
    console.log(`\n  Books found (${books.length}):`);
    books.forEach(b => console.log(`    • ${b.title} [${b.status}] ${b.wordsCurrent ? b.wordsCurrent.toLocaleString()+' words' : ''}`));
  }

  console.log('\n  Open book-machine-local.html in Chrome/Edge — the ⚡ badge will go green.');
  console.log('  Press Ctrl+C to stop.\n');
});

server.on('error', e => {
  if (e.code === 'EADDRINUSE') {
    console.error(`\n  ✗ Port ${PORT} is already in use.`);
    console.error('  If another server is running, stop it first (Ctrl+C in that window).\n');
  } else {
    console.error('\n  Server error:', e.message);
  }
  process.exit(1);
});
