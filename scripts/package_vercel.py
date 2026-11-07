"""Copy the production frontend to Vercel's CDN-served public directory."""
from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
source=root/'frontend/dist'
target=root/'public'
if not (source/'index.html').is_file(): raise SystemExit('Build frontend before packaging')
shutil.copytree(source,target,dirs_exist_ok=True)
print('Packaged frontend and photographic fallbacks for Vercel')
