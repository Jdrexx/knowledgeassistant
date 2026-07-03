from __future__ import annotations
import json, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
APP_NAME='Local RAG Knowledge Assistant'
DB_FILE=Path(__file__).resolve().parent.parent/'data'/'app.sqlite'
DB_FILE.parent.mkdir(exist_ok=True)
app=FastAPI(title=APP_NAME, version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def db() -> sqlite3.Connection:
    conn=sqlite3.connect(DB_FILE); conn.row_factory=sqlite3.Row; conn.execute('pragma journal_mode=wal'); return conn
def init_db() -> None:
    with db() as conn: conn.execute('create table if not exists records (id integer primary key autoincrement, kind text not null, title text not null, payload text not null, created_at text not null)')
init_db()
def save_record(kind: str, title: str, payload: str) -> int:
    with db() as conn:
        cur=conn.execute('insert into records(kind,title,payload,created_at) values (?,?,?,?)',(kind,title,payload,datetime.now(timezone.utc).isoformat())); return int(cur.lastrowid)
def rows(kind: str | None = None) -> list[dict[str, Any]]:
    with db() as conn:
        data=conn.execute('select * from records where kind=? order by id desc',(kind,)).fetchall() if kind else conn.execute('select * from records order by id desc').fetchall()
    return [dict(r) for r in data]
@app.get('/api/health')
def health(): return {'ok': True, 'app': APP_NAME, 'records': len(rows())}
@app.get('/', response_class=HTMLResponse)
def home(): return INDEX_HTML

class IngestRequest(BaseModel):
    title: str
    text: str = Field(..., min_length=1)
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
def chunks(text: str, size: int = 90) -> list[str]:
    words=text.split(); return [' '.join(words[i:i+size]) for i in range(0, len(words), size)] or [text]
def score(q: str, chunk: str) -> int:
    return len(set(re.findall(r"[a-z0-9]+", q.lower())) & set(re.findall(r"[a-z0-9]+", chunk.lower())))
@app.post('/api/ingest')
def ingest(req: IngestRequest):
    ids=[save_record('chunk', f"{req.title} #{i}", ch) for i,ch in enumerate(chunks(req.text), start=1)]
    return {"chunks": len(ids), "ids": ids}
@app.post('/api/ask')
def ask(req: QuestionRequest):
    ranked=sorted(rows('chunk'), key=lambda r: score(req.question, r['payload']), reverse=True)[:3]
    citations=[{"title": r['title'], "excerpt": r['payload'][:280]} for r in ranked if score(req.question, r['payload'])>0]
    answer = "I found relevant notes: " + ' '.join(c['excerpt'] for c in citations[:2]) if citations else "No strong matching document chunk found yet. Ingest more source material."
    return {"answer": answer, "citations": citations}

INDEX_HTML='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local RAG Knowledge Assistant</title><style>body{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0}main{max-width:980px;margin:auto;padding:32px}.card{background:#111827;border:1px solid #334155;border-radius:18px;padding:24px;margin:18px 0}h1{font-size:42px}textarea,input{width:100%;box-sizing:border-box;border-radius:12px;border:1px solid #475569;background:#020617;color:#e5e7eb;padding:14px;margin:8px 0}button{background:#22c55e;color:#04130a;border:0;border-radius:12px;padding:12px 18px;font-weight:700}pre{white-space:pre-wrap;background:#020617;border-radius:12px;padding:16px}.pill{background:#1e293b;border:1px solid #475569;border-radius:999px;padding:6px 10px}</style></head><body><main><div class="card"><span class="pill">private knowledge search</span><h1>Local RAG Knowledge Assistant</h1><p>Upload notes/docs, chunk them, search relevant passages, and answer questions with citations.</p><ul><li>Document ingestion</li><li>Chunked keyword retrieval</li><li>Question answering with citations</li><li>Local-first architecture</li><li>SQLite-backed document store</li></ul></div><div class="card"><h2>Live API Demo</h2><textarea id="input" rows="7">FastAPI supports Python APIs and automatic documentation for backend services.</textarea><textarea id="input2" rows="4">What supports Python APIs?</textarea><button onclick="runDemo()">Run Demo</button><pre id="out">Click Run Demo to call the FastAPI backend.</pre></div><div class="card"><h2>API</h2><p>Health: <code>/api/health</code> · Docs: <code>/docs</code></p></div><script>async function runDemo(){const res = await (fetch(\'/api/ingest\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({title:\'Demo Doc\',text:document.getElementById(\'input\').value})}).then(()=>fetch(\'/api/ask\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({question:document.getElementById(\'input2\').value})}))); const data = await res.json(); document.getElementById(\'out\').textContent = JSON.stringify(data,null,2);}</script></main></body></html>'
