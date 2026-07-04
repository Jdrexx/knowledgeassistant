from __future__ import annotations
import json, re, sqlite3
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

APP_NAME='Local RAG Knowledge Assistant'
DB_FILE=Path(__file__).resolve().parent.parent/'data'/'app.sqlite'
DB_FILE.parent.mkdir(exist_ok=True)
app=FastAPI(title=APP_NAME, version='0.2.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Optional Ollama integration
_ollama = None
try:
    import ollama as _ollama
    _ollama_available = True
except ImportError:
    _ollama_available = False

def db() -> sqlite3.Connection:
    conn=sqlite3.connect(DB_FILE); conn.row_factory=sqlite3.Row; conn.execute('pragma journal_mode=wal'); return conn

def init_db() -> None:
    with db() as conn:
        conn.execute('create table if not exists records (id integer primary key autoincrement, kind text not null, title text not null, payload text not null, embedding text, created_at text not null)')
        # Migrate: add embedding column if missing in existing DB
        cols=[c[1] for c in conn.execute('pragma table_info(records)').fetchall()]
        if 'embedding' not in cols:
            conn.execute('alter table records add column embedding text')
init_db()

def save_record(kind: str, title: str, payload: str, embedding: str | None = None) -> int:
    with db() as conn:
        cur=conn.execute('insert into records(kind,title,payload,embedding,created_at) values (?,?,?,?,?)',(kind,title,payload,embedding,datetime.now(timezone.utc).isoformat()))
        return int(cur.lastrowid)

def rows(kind: str | None = None) -> list[dict[str, Any]]:
    with db() as conn:
        data=conn.execute('select * from records where kind=? order by id desc',(kind,)).fetchall() if kind else conn.execute('select * from records order by id desc').fetchall()
    return [dict(r) for r in data]

@app.get('/api/health')
def health(): return {'ok': True, 'app': APP_NAME, 'records': len(rows()), 'ollama_available': _ollama_available}

@app.get('/', response_class=HTMLResponse)
def home(): return INDEX_HTML

class IngestRequest(BaseModel):
    title: str
    text: str = Field(..., min_length=1)
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)

# Chunking
def chunks(text: str, size: int = 90) -> list[str]:
    words=text.split(); return [' '.join(words[i:i+size]) for i in range(0, len(words), size)] or [text]

# Embedding via Ollama
def get_embedding(text: str) -> list[float] | None:
    try:
        resp = _ollama.embeddings(model='nomic-embed-text', prompt=text)
        return resp['embedding']
    except Exception:
        return None

def cosine_sim(a: list[float], b: list[float]) -> float:
    dot=sum(x*y for x,y in zip(a,b)); na=sqrt(sum(x*x for x in a)); nb=sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0.0

# Keyword fallback
def keyword_score(q: str, chunk: str) -> int:
    return len(set(re.findall(r"[a-z0-9]+", q.lower())) & set(re.findall(r"[a-z0-9]+", chunk.lower())))

@app.post('/api/ingest')
def ingest(req: IngestRequest):
    chs = chunks(req.text)
    full_emb = get_embedding(req.text)
    emb_json = json.dumps(full_emb) if full_emb else None
    ids=[save_record('chunk', f"{req.title} #{i}", ch, emb_json) for i,ch in enumerate(chs, start=1)]
    return {"chunks": len(ids), "ids": ids, "retrieval": "ollama/nomic-embed-text" if full_emb else "keyword"}

@app.post('/api/ask')
def ask(req: QuestionRequest):
    all_chunks = rows('chunk')
    if not all_chunks:
        return {"answer": "No documents have been ingested yet.", "citations": [], "retrieval": "none"}
    q_emb = get_embedding(req.question)

    if q_emb:
        scored = [(cosine_sim(q_emb, json.loads(r['embedding'])) if r.get('embedding') else 0.0, r) for r in all_chunks]
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [r for s,r in scored[:5] if s > 0.15]
        if not ranked:
            ranked = [r for _,r in scored[:3]]
        retrieval = "embedding"
    else:
        ranked = sorted(all_chunks, key=lambda r: keyword_score(req.question, r['payload']), reverse=True)[:5]
        retrieval = "keyword"

    citations=[{"title": r['title'], "excerpt": r['payload'][:280]} for r in ranked[:3]]
    if citations and _ollama_available and q_emb:
        try:
            ctx='\n'.join(c['excerpt'] for c in citations[:3])
            resp=_ollama.chat(model='llama3.2:3b', messages=[
                {"role":"system","content":"Answer concisely based only on the provided context."},
                {"role":"user","content":f"Context:\n{ctx}\n\nQuestion: {req.question}"}
            ])
            answer=resp['message']['content']
        except Exception:
            answer = "Relevant notes found: " + ' | '.join(c['excerpt'][:120] for c in citations[:2])
    else:
        answer = "Relevant notes found: " + ' | '.join(c['excerpt'][:120] for c in citations[:2]) if citations else "No matching document chunk found. Ingest more source material."

    return {"answer": answer, "citations": citations, "retrieval": retrieval}

INDEX_HTML='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local RAG Knowledge Assistant (Ollama)</title><style>body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0}main{max-width:980px;margin:auto;padding:32px}.card{background:#111827;border:1px solid #334155;border-radius:18px;padding:24px;margin:18px 0}h1{font-size:42px}textarea,input{width:100%;box-sizing:border-box;border-radius:12px;border:1px solid #475569;background:#020617;color:#e5e7eb;padding:14px;margin:8px 0}button{background:#22c55e;color:#04130a;border:0;border-radius:12px;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#020617;border-radius:12px;padding:16px}.pill{background:#1e293b;border:1px solid #475569;border-radius:999px;padding:6px 10px}</style></head><body><main><div class="card"><span class="pill">local RAG · Ollama</span><h1>Local RAG Knowledge Assistant</h1><p>Upload notes/docs, chunk them, search relevant passages, and answer questions with citations. Uses Ollama embeddings + LLM when available; falls back to keyword search.</p><ul><li>Document ingestion with embedding</li><li>Cosine-similarity retrieval (Ollama nomic-embed-text)</li><li>LLM-powered answer generation (Ollama llama3.2)</li><li>Keyword fallback when Ollama is offline</li><li>SQLite-backed document store</li></ul></div><div class="card"><h2>Live API Demo</h2><textarea id="input" rows="7">FastAPI supports Python APIs and automatic documentation for backend services.</textarea><textarea id="input2" rows="4">What supports Python APIs?</textarea><button onclick="runDemo()">Run Demo</button><pre id="out">Click Run Demo to call the FastAPI backend.</pre></div><div class="card"><h2>API</h2><p>Health: <code>/api/health</code> · Docs: <code>/docs</code></p></div><script>async function runDemo(){const res = await (fetch(\'/api/ingest\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({title:\'Demo Doc\',text:document.getElementById(\'input\').value})}).then(()=>fetch(\'/api/ask\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({question:document.getElementById(\'input2\').value})}))); const data = await res.json(); document.getElementById(\'out\').textContent = JSON.stringify(data,null,2);}</script></main></body></html>'
