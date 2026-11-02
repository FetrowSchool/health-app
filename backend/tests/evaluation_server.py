"""Explicit evaluation-only server: fictional SQLite, mock provider, no live voice."""
import asyncio
import json
import os
from pathlib import Path
from fastapi.responses import JSONResponse
from backend.app.main import create_app
from backend.app.config import Settings, PROJECT_ROOT
from backend.app.providers import MockProvider, ProviderFailure

root=Path(os.environ['PAUSE_EVAL_DIR']).resolve()
if root==PROJECT_ROOT or PROJECT_ROOT in root.parents:
    raise RuntimeError('Use a temporary directory outside the project.')
root.mkdir(parents=True,exist_ok=True)


class EvaluationProvider(MockProvider):
    async def generate(self,context):
        if (root/'feedback_failure').exists():raise ProviderFailure('provider_error')
        return await super().generate(context)


app=create_app(Settings(database_path=root/'evaluation.sqlite3',model_provider='mock'),EvaluationProvider())


@app.middleware('http')
async def mocked_voice(request,call_next):
    path=request.url.path
    if path=='/api/voice/config':return JSONResponse({'status':'configured','duration_seconds':60})
    if path=='/api/voice/sessions':
        counts=root/'mock-session-count.json'
        count=json.loads(counts.read_text()) if counts.exists() else {'mock_session_posts':0,'real_provider_calls':0}
        count['mock_session_posts']+=1;counts.write_text(json.dumps(count))
        await asyncio.sleep(2)
        if (root/'voice_failure').exists():return JSONResponse({'detail':'Fictional provider failure.'},status_code=503)
        return JSONResponse({'session_id':'evaluation-session','sdp':'v=0\r\nevaluation-answer','duration_seconds':60},status_code=201)
    if path=='/api/voice/sessions/close':return JSONResponse({'status':'close_requested'})
    return await call_next(request)
