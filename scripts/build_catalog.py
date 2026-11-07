"""Curated real-photography families. Related synthetic SKUs share their family photo.

No search/random image endpoints. Gallery views are explicitly labeled full-frame
and detail crops of the SAME photograph, never invented alternate product angles.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# key, product name, category, node, price, provider photo ID, framing
FAMILIES = [
    ('headphones','Studio Wireless Headphones','Electronics','techhaven',129,'u:1505740420928-5e560c06d30e','contain'),
    ('tote','Everyday Canvas Tote','Fashion','atelier',38,'p:9869067','contain'),
    ('pourover','Ceramic Pour-over Set','Home & Kitchen','earthgoods',64,'p:11206191','contain'),
    ('trail-shoes','Trail Runner Sneakers','Sports','atelier',95,'p:2529148','contain'),
    ('speaker','Portable Bluetooth Speaker','Electronics','techhaven',79,'p:7772558','contain'),
    ('blanket','Linen Throw Blanket','Home & Kitchen','earthgoods',89,'p:11125918','cover'),
    ('bottle','Recycled Steel Bottle','Sports','earthgoods',29,'p:2832062','contain'),
    ('lamp','Minimal Desk Lamp','Home & Kitchen','techhaven',59,'p:1112598','contain'),
    ('laptop','Everyday Laptop','Electronics','techhaven',899,'u:1496181133206-80ce9b88a853','contain'),
    ('smartphone','Essential Smartphone','Electronics','techhaven',499,'u:1511707171634-5f897ff02aa9','contain'),
    ('smartwatch','Active Smartwatch','Electronics','techhaven',189,'u:1546868871-7041f2a55e12','contain'),
    ('camera','Creator Digital Camera','Electronics','techhaven',649,'p:15945023','contain'),
    ('shirt','Relaxed Everyday Shirt','Fashion','atelier',49,'p:11671275','contain'),
    ('handbag','Signature Handbag','Fashion','atelier',119,'u:1548036328-c9fa89d128fa','contain'),
    ('dress','Classic Evening Dress','Fashion','atelier',89,'p:19895958','contain'),
    ('backpack','Everyday Travel Backpack','Fashion','atelier',79,'u:1553062407-98eeb64c6a62','contain'),
    ('sneakers','Everyday Low-top Sneakers','Fashion','atelier',85,'u:1525966222134-fcfa99b8ae77','contain'),
    ('coffee-maker','Morning Drip Coffee Maker','Home & Kitchen','earthgoods',129,'p:8937258','contain'),
    ('blender','Kitchen Countertop Blender','Home & Kitchen','earthgoods',99,'p:7460165','contain'),
    ('chair','Modern Accent Chair','Home & Kitchen','earthgoods',249,'u:1598300042247-d088f8ab3a91','contain'),
    ('sofa','Everyday Lounge Sofa','Home & Kitchen','earthgoods',799,'u:1555041469-a586c61ea9bc','contain'),
    ('skincare','Daily Skincare Collection','Beauty','earthgoods',59,'p:4841386','contain'),
    ('serum','Face Serum Collection','Beauty','earthgoods',39,'p:8100778','contain'),
    ('perfume','Signature Perfume','Beauty','atelier',79,'p:9202849','contain'),
    ('lipstick','Essential Lipstick Trio','Beauty','atelier',29,'p:7256082','contain'),
    ('dumbbells','Hex Dumbbell Pair','Sports','earthgoods',69,'p:29224210','contain'),
    ('yoga','Everyday Yoga Mat','Sports','earthgoods',39,'p:8939851','contain'),
    ('basketball','Court Basketball','Sports','earthgoods',35,'p:19932843','contain'),
    ('tennis','Court Tennis Racket','Sports','atelier',89,'p:8224531','contain'),
    ('running-shoes','Daily Running Shoes','Sports','atelier',109,'u:1542291026-7eec264c27ff','contain'),
]


def photo_url(ref, width=1200, detail=False):
    provider, photo_id = ref.split(':')
    base = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg' if provider=='p' else f'https://images.unsplash.com/photo-{photo_id}'
    # Fixed source ID, no random subject assignment.
    params = f'auto=compress&cs=tinysrgb&w={width}' if provider=='p' else f'auto=format&fit=max&w={width}&q=85'
    if detail:
        params += '&h='+str(width)+'&fit=crop&crop=center'
    return base+'?'+params


def build():
    products, media, families = [], {}, {}
    for key,name,category,node,price,ref,fit in FAMILIES:
        provider, pid = ref.split(':')
        source = f'https://www.pexels.com/photo/{pid}/' if provider=='p' else f'https://unsplash.com/photos/{pid}'
        # Unsplash CDN original is a stable, directly attributable image source.
        if provider=='u': source=photo_url(ref,1800)
        item=dict(family=key,images=[dict(url=photo_url(ref),label='Full photograph',fit=fit),dict(url=photo_url(ref,1600,True),label='Detail crop',fit='cover')],fallback=f'/product-images/{key}.webp',source_url=source)
        families[key]={**item,'name':name,'category':category,'reference':ref}
        for variant in range(1,11):
            product_id=f'{key}-{variant:02d}'
            products.append([product_id,f'{name} — Collection {variant:02d}',node,category,round(price*(1+(variant-1)*.025),2),'',f'A considered {name.lower()} for your everyday. Collection {variant:02d}.'])
            media[product_id]=item
    keys=[f[0] for f in FAMILIES]
    products.sort(key=lambda p:(int(p[0].rsplit('-',1)[1]),(keys.index(p[0].rsplit('-',1)[0])-8)%len(keys)))
    # Existing IDs and prices stay stable for existing carts and orders.
    for i,(key,*_) in enumerate(FAMILIES[:8],1): media[f'p{i}']=families[key]
    target=ROOT/'backend/data/product-media.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(dict(products=products,media=media),indent=2),encoding='utf-8')
    target=ROOT/'frontend/src/product-photos.json'
    target.write_text(json.dumps(families,indent=2),encoding='utf-8')
    print(f'{len(products)+8} products; {len(families)} subject-specific photography families')

if __name__=='__main__': build()
