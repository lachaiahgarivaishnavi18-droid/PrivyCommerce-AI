"""Verify every unique catalog photo URL; keep same-photo fallbacks in Vercel public/.

Run with --download to provision snapshots. PIL verifies that responses are
decodable, genuinely high-resolution raster images, not error pages.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import time
import re
import requests
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]

def verify(download=False,responsive=False):
    families=json.loads((ROOT/'frontend/src/product-photos.json').read_text())
    out=ROOT/'frontend/public/product-images'
    out.mkdir(parents=True,exist_ok=True)
    def check(pair):
        key,item=pair
        results=[]
        images=list(item['images'])
        if responsive:
            for image in item['images']:
                for width in [480,800,1200,1800]:
                    url=re.sub(r'([?&])w=\d+',lambda m:m[1]+'w='+str(width),image['url'])
                    url=re.sub(r'([?&])h=\d+',lambda m:m[1]+'h='+str(width),url)
                    if url not in [i['url'] for i in images]: images.append(dict(url=url))
        for i,image in enumerate(images):
            for attempt in range(3):
                try:
                    response=requests.get(image['url'],timeout=40)
                    response.raise_for_status()
                    im=Image.open(BytesIO(response.content));im.load()
                    if min(im.size)<(250 if responsive else 500): raise ValueError(f'Image too small: {im.size}')
                    if download and i==0:
                        im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1400,1400))
                        im.save(out/f'{key}.webp','WEBP',quality=88)
                    results.append(dict(family=key,url=image['url'],status=response.status_code,width=im.width,height=im.height))
                    break
                except Exception as e:
                    if attempt==2: return [dict(family=key,url=image['url'],error=str(e))]
                    time.sleep(1)
        return results
    with ThreadPoolExecutor(max_workers=5) as pool:
        results=[r for rows in pool.map(check,families.items()) for r in rows]
    report=dict(checked_at=datetime.now(timezone.utc).isoformat(),products=308,unique_urls=len(results),results=results)
    (ROOT/'image-verification.json').write_text(json.dumps(report,indent=2))
    if download:
        sheet=Image.new('RGB',(1200,((len(families)+4)//5)*210),'white')
        draw=ImageDraw.Draw(sheet)
        for i,(key,item) in enumerate(families.items()):
            path=out/f'{key}.webp'
            if path.exists():
                im=Image.open(path);im=ImageOps.contain(im,(230,180))
                sheet.paste(im,((i%5)*240+(230-im.width)//2,(i//5)*210))
            draw.text(((i%5)*240+8,(i//5)*210+185),key,fill='black')
        sheet.save(ROOT/'product-contact-sheet.jpg',quality=90)
    errors=[r for r in results if 'error' in r]
    print(json.dumps(dict(verified=len(results)-len(errors),errors=errors)))
    if errors: raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true');parser.add_argument('--responsive',action='store_true')
    args=parser.parse_args()
    verify(args.download,args.responsive)
