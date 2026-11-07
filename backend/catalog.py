"""Presentation-only catalog expansion and media; customer data is never touched."""
import json
from pathlib import Path
from sqlalchemy import text

DATA = json.loads((Path(__file__).parent / 'data' / 'product-media.json').read_text(encoding='utf-8'))
EXTRA_PRODUCTS = [tuple(p) for p in DATA['products']]


def initialize_media(connection):
    connection.execute(text('CREATE TABLE IF NOT EXISTS product_media (product_id TEXT PRIMARY KEY, family TEXT, images TEXT, fallback TEXT, source_url TEXT)'))
    for product_id, media in DATA['media'].items():
        connection.execute(text('INSERT INTO product_media (product_id,family,images,fallback,source_url) VALUES (:id,:family,:images,:fallback,:source) ON CONFLICT (product_id) DO UPDATE SET family=:family,images=:images,fallback=:fallback,source_url=:source'),
                           dict(id=product_id,family=media['family'],images=json.dumps(media['images']),fallback=media['fallback'],source=media['source_url']))


def media_records(engine):
    with engine.connect() as connection:
        return {r['product_id']: dict(image_url=json.loads(r['images'])[0]['url'], images=json.loads(r['images']), fallback_image=r['fallback'], image_source=r['source_url'], family=r['family']) for r in connection.execute(text('SELECT * FROM product_media')).mappings()}
