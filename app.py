"""Vercel entrypoint. Reuses the existing API and serves the built React app."""
import os
from pathlib import Path

if os.getenv('VERCEL'):
    database_url=os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    if not database_url:
        raise RuntimeError('Connect a PostgreSQL database and set DATABASE_URL before deploying.')
    if database_url.startswith(('postgres://','postgresql://')):
        database_url='postgresql+psycopg://'+database_url.split('://',1)[1]
    os.environ['DATABASE_URL']=database_url
    os.environ.setdefault('COOKIE_SECURE','true')
    origin=os.getenv('VERCEL_PROJECT_PRODUCTION_URL') or os.getenv('VERCEL_URL')
    if origin: os.environ.setdefault('FRONTEND_URL','https://'+origin)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from backend.main import app

PUBLIC=Path(__file__).resolve().parent/'public'

@app.get('/{path:path}',include_in_schema=False)
def frontend(path:str):
    if path.startswith('api/'):
        raise HTTPException(404,'API route not found')
    target=(PUBLIC/path).resolve()
    if target.is_relative_to(PUBLIC.resolve()) and target.is_file():
        return FileResponse(target)
    index=PUBLIC/'index.html'
    if not index.exists(): raise HTTPException(503,'Frontend build is unavailable')
    return FileResponse(index)
