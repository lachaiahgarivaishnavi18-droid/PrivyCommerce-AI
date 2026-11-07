import {useEffect,useRef,useState,type ReactNode} from 'react';
import {Link} from 'react-router-dom';
import {ArrowLeft,ArrowRight,Check,Maximize2,Plus,ShieldCheck,SlidersHorizontal,X} from 'lucide-react';
import photos from './product-photos.json';

export type Product={id:string;name:string;node:string;category:string;price:number;description:string;family?:string;image_url?:string;images?:{url:string;label:string;fit:string}[];fallback_image?:string;image_source?:string};
export const department=(p:Product)=>({'Home':'Home & Kitchen','Accessories':'Fashion','Footwear':'Sports','Lifestyle':'Sports'}[p.category]||p.category);
const originals=['headphones','tote','pourover','trail-shoes','speaker','blanket','bottle','lamp'];
export function photography(p:Product){
 const family=p.family||originals[Number(p.id.slice(1))-1];
 const local=(photos as Record<string,any>)[family];
 return {images:p.images||local?.images||[],fallback:p.fallback_image||local?.fallback,source:p.image_source||local?.source_url};
}

export function ProductImage({product,index=0,eager=false,className='',large=false}:{product:Product;index?:number;eager?:boolean;className?:string;large?:boolean}){
 const media=photography(product),image=media.images[index]||media.images[0];
 const [stage,setStage]=useState(0),[loaded,setLoaded]=useState(false);
 const imageRef=useRef<HTMLImageElement>(null);
 // Cached images can finish before React's effect runs; preserve that completion.
 useEffect(()=>{setStage(0);setLoaded(!!imageRef.current?.complete&&imageRef.current.naturalWidth>0)},[product.id,index]);
 const source=stage===1?media.fallback:image?.url;
 const resize=(url:string,w:number)=>url.replace(/([?&])w=\d+/,`$1w=${w}`).replace(/([?&])h=\d+/,`$1h=${w}`);
 if(!source||stage>1)return <div className={'photo-unavailable '+className} role="img" aria-label={product.name+' photograph unavailable'}><span>Photograph temporarily unavailable</span><button onClick={()=>{setStage(0);setLoaded(false)}}>Retry photo</button></div>;
 return <div className={'photo-frame '+(loaded?'is-loaded ':'')+className}>
   <img ref={imageRef} src={source} srcSet={stage===0?`${resize(source,480)} 480w, ${resize(source,800)} 800w, ${resize(source,large?1800:1200)} ${large?1800:1200}w`:undefined} sizes={large?'(max-width: 760px) 100vw, 60vw':'(max-width: 760px) 46vw, (max-width: 1150px) 27vw, 23vw'} alt={`${product.name} — ${stage===1?'full photograph':image.label}`} width="1200" height="1200" loading={eager?'eager':'lazy'} decoding="async" fetchPriority={eager?'high':'auto'} style={{objectFit:stage===1?'contain':image.fit as 'contain'|'cover'}} onLoad={()=>setLoaded(true)} onError={()=>{setLoaded(false);setStage(v=>v+1)}}/>
 </div>;
}

export function ProductCard({product,onAdd,onCompare,selected=false,eager=false}:{product:Product;onAdd:(p:Product)=>void;onCompare:(p:Product)=>void;selected?:boolean;eager?:boolean}){
 return <article className="product photo-product">
  <Link className="product-photo-link" to={'/products/'+product.id} aria-label={'View '+product.name}><ProductImage product={product} eager={eager}/><span className="view-product">Explore product <ArrowRight size={14}/></span></Link>
  <div className="product-info"><div className="eyebrow">{department(product)} <span>· {product.node}</span></div><Link to={'/products/'+product.id}><h3>{product.name}</h3></Link><p>{product.description}</p><div className="price-row"><strong>${product.price.toFixed(2)}</strong><button className="add" aria-label={'Add '+product.name+' to bag'} onClick={()=>onAdd(product)}><Plus size={17}/><span>Add</span></button></div><button className={'compare-choice '+(selected?'chosen':'')} aria-pressed={selected} onClick={()=>onCompare(product)}><span>{selected?<Check size={11}/>:<Plus size={11}/>}</span>{selected?'Selected for comparison':'Compare'}</button></div>
 </article>;
}

function Lightbox({product,index,onClose}:{product:Product;index:number;onClose:()=>void}){
 const dialog=useRef<HTMLDialogElement>(null);
 const [active,setActive]=useState(index);
 const images=photography(product).images;
 useEffect(()=>{dialog.current?.showModal();const prior=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{document.body.style.overflow=prior}},[]);
 return <dialog ref={dialog} className="photo-lightbox" onCancel={onClose} onClick={e=>{if(e.target===e.currentTarget)onClose()}}><div className="lightbox-top"><div><strong>{product.name}</strong><small>{images[active].label} · {active+1} / {images.length}</small></div><button autoFocus aria-label="Close enlarged photo" onClick={onClose}><X/></button></div><ProductImage product={product} index={active} eager large/>
 <div className="lightbox-controls"><button className="outline" aria-label="Previous photograph" onClick={()=>setActive(v=>(v+images.length-1)%images.length)}><ArrowLeft size={17}/></button><span>{images[active].label}</span><button className="outline" aria-label="Next photograph" onClick={()=>setActive(v=>(v+1)%images.length)}><ArrowRight size={17}/></button></div></dialog>;
}

export function ProductDetail({product,allProducts,onAdd,onCompare,selected,cards}:{product:Product;allProducts:Product[];onAdd:(p:Product)=>void;onCompare:(p:Product)=>void;selected:boolean;cards:(p:Product[])=>ReactNode}){
 const [active,setActive]=useState(0),[zoom,setZoom]=useState(false);
 const media=photography(product);
 useEffect(()=>{setActive(0);setZoom(false)},[product.id]);
 const related=allProducts.filter(p=>p.id!==product.id&&department(p)===department(product)&&p.family!==product.family).slice(0,4);
 return <><Link className="back-to-shop" to="/"><ArrowLeft size={15}/> Back to the collection</Link><section className="product-detail"><div className="gallery"><button className="gallery-main" onClick={()=>setZoom(true)} aria-label={'Enlarge '+product.name+' photograph'}><ProductImage product={product} index={active} eager large/><span className="zoom-hint"><Maximize2 size={15}/> Click to enlarge</span></button><div className="gallery-thumbnails" aria-label="Product image gallery">{media.images.map((im:any,i:number)=><button key={im.url} className={active===i?'active':''} aria-label={'Show '+im.label} aria-pressed={active===i} onClick={()=>setActive(i)}><ProductImage product={product} index={i} eager/><span>{im.label}</span></button>)}</div><p className="photo-caption">Real product photography · Full image and a closer crop of the same photograph.</p></div><div className="detail-copy"><div className="eyebrow green">THE {department(product).toUpperCase()} EDIT</div><h1>{product.name}</h1><p className="detail-description">{product.description}</p><div className="detail-price">${product.price.toFixed(2)} <small>USD · Demo catalog</small></div><div className="detail-rule"/><dl><div><dt>Collection</dt><dd>{department(product)}</dd></div><div><dt>Commerce partner</dt><dd>{product.node}</dd></div><div><dt>Product reference</dt><dd>{product.id}</dd></div></dl><button className="primary detail-add" onClick={()=>onAdd(product)}><Plus size={18}/> Add to your bag <ArrowRight size={17}/></button><button className="outline detail-compare" aria-pressed={selected} onClick={()=>onCompare(product)}><SlidersHorizontal size={16}/>{selected?'Selected for comparison':'Add to comparison'}</button><div className="detail-privacy"><ShieldCheck size={19}/><div><strong>A good find. A private experience.</strong><p>Your preferences are only saved with your permission.</p></div></div><p className="catalog-disclosure">Synthetic research product. Stock photography represents the product family; collection variants share the same product-family photograph. No purchase or payment is completed.</p><a className="photo-credit" href={media.source} target="_blank" rel="noreferrer">View original photograph ↗</a></div></section>{related.length>0&&<section className="related-products"><div className="section-heading"><div><div className="eyebrow green">KEEP EXPLORING</div><h2>You might also like</h2></div><Link className="text-button" to="/">Shop all finds <ArrowRight size={14}/></Link></div><div className="product-grid">{cards(related)}</div></section>}{zoom&&<Lightbox product={product} index={active} onClose={()=>setZoom(false)}/>}</>;
}

export function ProductComparison({products,onAdd,onRemove}:{products:Product[];onAdd:(p:Product)=>void;onRemove:(p:Product)=>void}){
 return <><div className="page-heading"><div><div className="eyebrow green">FIND YOUR BEST FIT</div><h1>A closer look, side by side.</h1><p>Compare up to four finds before choosing your favorite.</p></div><Link className="outline" to="/">Continue exploring <ArrowRight size={15}/></Link></div>{products.length?<div className="comparison-scroll"><div className="comparison-grid" style={{gridTemplateColumns:`repeat(${products.length},minmax(220px,1fr))`}}>{products.map(p=><article className="comparison-product" key={p.id}><button className="compare-remove" aria-label={'Remove '+p.name+' from comparison'} onClick={()=>onRemove(p)}><X size={17}/></button><Link to={'/products/'+p.id}><ProductImage product={p} eager/><h2>{p.name}</h2></Link><strong className="comparison-price">${p.price.toFixed(2)}</strong><dl><dt>Collection</dt><dd>{department(p)}</dd><dt>Commerce partner</dt><dd>{p.node}</dd><dt>About this find</dt><dd>{p.description}</dd></dl><button className="primary" onClick={()=>onAdd(p)}>Add to bag <Plus size={16}/></button></article>)}</div></div>:<div className="empty"><SlidersHorizontal size={35}/><h2>A little perspective helps.</h2><p>Select Compare on any product card to see your finds here.</p><Link to="/" className="primary">Explore the collection</Link></div>}</>;
}
