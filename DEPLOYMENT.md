# Vercel production deployment

Production URL: https://privycommerce-ai-20261105.vercel.app

The repository root is the Vercel project root. `vercel.json` selects the FastAPI framework; `app.py` reuses the existing backend. The cloud build compiles `frontend`, then copies the output to the CDN-served root `public` directory. Explicit SPA rewrites keep product details and dashboard deep links working while preserving `/api/*` routes.

A free-plan Neon PostgreSQL resource, `privycommerce-ai-db`, is connected to this project's production environment. Its credentials are managed by the Vercel integration, never committed. `app.py` converts standard PostgreSQL connection URLs to SQLAlchemy's psycopg driver, enables Secure cookies, and uses Vercel's production hostname for origin validation. A production deployment fails rather than falling back to nonpersistent SQLite when the database environment variable is missing.

Existing local SQLite accounts and customer records are excluded from uploads. Create a new account on the live site. The deterministic shopping assistant works without an LLM key; optional provider keys belong in server-side Vercel environment variables.

To update the existing deployment from the linked repository root:

```powershell
vercel deploy --prod
```

In this workspace, the official CLI is also available through:

```powershell
node frontend/.tools/vercel/node_modules/vercel/dist/index.js deploy --prod --yes
```

Verify an owned deployment with a new synthetic test customer:

```powershell
.\.venv\Scripts\python scripts/verify_deployment.py https://privycommerce-ai-20261105.vercel.app
```

This verifies live frontend routes, the API, photographic fallback delivery, account registration, Secure session cookies, cart updates, shopping recommendations with photos, demo checkout, persistent order retrieval after reauthentication, and logout. It creates one synthetic customer and demo order, collects no payment, and prints no credentials.
