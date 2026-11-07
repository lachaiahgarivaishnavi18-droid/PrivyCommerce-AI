# Product photography

The catalog contains 308 synthetic products and 30 visually reviewed photographic product families across Electronics, Fashion, Home & Kitchen, Beauty, and Sports. Existing IDs `p1`–`p8`, categories and prices remain stable. Ten related synthetic collection SKUs per family intentionally reuse that family's image; unrelated families never share images. These are research catalog variants, not 308 separately photographed real commercial items. Visible product details disclose this distinction.

Photography comes from fixed Pexels and Unsplash photo URLs, not random or keyword image endpoints. The complete subject mapping and original source links live in `scripts/build_catalog.py`, `backend/data/product-media.json`, and `frontend/src/product-photos.json`. Sources are linked on every product-detail page. These are legitimate stock photographs of real objects; no images were generated with AI. Pexels photo licensing: https://www.pexels.com/license/ . Unsplash photo licensing: https://unsplash.com/license . Stock photography does not imply a partnership with pictured brands.

The gallery supports multiple image records, selectable thumbnails and an enlarged native-dialog preview, with keyboard navigation through buttons and Escape dismissal. The current seeded views are a full photograph and a closer crop of that same photograph, explicitly labeled; they do not pretend to be independently photographed product angles. Future genuine additional product photographs can be added to each `images` list without changing the UI.

The only database addition is the independent `product_media` table and Alembic migration `002`. Existing customer tables, authentication, consent, federation, agent graph, cart and order algorithms are unchanged. `/api/products` retains its existing fields and filters and adds media metadata; chat recommendations carry that same metadata. No existing API route is removed. The media initializer is idempotent and stores image URLs persistently.

All image surfaces use the same `ProductImage` component: discovery cards, AI recommendations, product details, comparison, cart and order history. It uses explicit dimensions, responsive `srcset`, lazy loading and appropriate cover/contain treatment. If the remote photo fails, it loads the same product-family photograph from `public/product-images/*.webp`. If both fail, an accessible text state offers Retry; it never substitutes an unrelated product or emoji. Local fallback files ship with the Vite/Vercel build. Remote image URLs are HTTPS, have no expiring tokens, and require no client API key. No Next.js image-domain configuration is needed for ordinary HTML images in this Vite application.

To regenerate metadata:

```powershell
.\.venv\Scripts\python scripts/build_catalog.py
```

To verify all distinct photo URLs, decode and check their resolution, and refresh local backups:

```powershell
.\.venv\Scripts\python -m pip install -r scripts/requirements-images.txt
.\.venv\Scripts\python scripts/verify_product_images.py --download --responsive
```

`image-verification.json` records the actual URL results and dimensions. `product-contact-sheet.jpg` is the visual QA contact sheet. Re-run validation when changing providers or photos. Live Vercel deployment is not part of local verification: verify the hosted build separately when deployed.

## Verified locally

- Six backend regression and media-coverage tests pass.
- TypeScript and Vite production build passes; all 30 local WebP backups are bundled.
- 270 source, gallery and responsive image URLs returned valid raster images; no broken URLs.
- Browser checks: discovery, category filtering, product details, full/detail gallery selection, enlarged dialog and Escape, comparison, cart photo and quantity controls, and AI recommendation photos.
- Mobile product and chat layouts checked at a narrow viewport; desktop checked with four columns. No document horizontal overflow.
- Cached-image visibility and live-preview root reuse fixes verified.
- Live Vercel deployment has not been performed.
