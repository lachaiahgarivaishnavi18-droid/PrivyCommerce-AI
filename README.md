# PrivyCommerce AI

Privacy-aware conversational commerce with three isolated store partitions, explicit customer memory, a LangGraph shopping workflow, and a NumPy federated-learning experiment.

Live application: [PrivyCommerce AI](https://privycommerce-ai-20261105.vercel.app).

See [deployment instructions](DEPLOYMENT.md) and [product photography documentation](PHOTOGRAPHY.md).

## Local setup

Use Python 3.12+ and Node 22+. From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API documentation: http://localhost:8000/docs.
If npm is unavailable in this particular workspace, the downloaded runner is `node .tools/package/bin/npm-cli.js` from `frontend`.

Create an account with a password of at least 10 characters. No API key is needed. Browse products, add them to your bag, and place a demo order. No payment is collected.

In Privacy center, enable collection and optionally personalization. Save a category such as `Electronics` in My memory for a selected store, then ask the assistant at that store. Collection, personalization, and federation are separate permissions, disabled by default. Export, edit, delete, pause, and audit controls call real backend APIs.

## Verification

```powershell
.\.venv\Scripts\python -m pytest backend/tests -q
cd frontend
npm run build
```

Tests exercise checkout, login/session revocation, consent denial and revocation, tenant isolation, origin checks, optimistic memory versions, and FedAvg convergence.

## Architecture

- React + TypeScript + Vite + Tailwind, React Router, Axios, Lucide, Recharts.
- FastAPI + Pydantic, SQLAlchemy connections, SQLite development or PostgreSQL production. Alembic initial schema migration; startup also creates missing tables for an easy demonstration.
- Central product catalog with 308 synthetic products and 30 curated real-photography families. See PHOTOGRAPHY.md for source provenance, gallery behavior, and fallback verification. Products and pricing are controlled by the backend.
- LangGraph catalog and recommendation agents, preceded by a consent gate. Agent traces are visible in chat. A deterministic keyword/category and budget recommender works offline. Optional OpenAI-compatible chat completion integration uses `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.
- Argon2 password hashing, random expiring HttpOnly session cookies with hashed server-side tokens, customer/admin checks, user-scoped data queries, audit trail, and basic single-process authentication throttling.
- Three registered node identities: `atelier`, `techhaven`, `earthgoods`. Raw memory uses the composite authorization boundary `(user_id, node)`. These are logical partitions within one database, not independently deployed services. The coordinator retrieves only permitted, minimized category analytics. Store adapters should become separate services for a physical federation.

## Research distinctions

**Federated customer memory:** versioned local store preferences, isolated by customer and node. Temporary conversation messages live in React state and are cleared with the conversation control or page reload. Messages are never automatically written to persistent memory.

**Federated analytics:** consent-gated per-node category counts for the signed-in customer. These exact counts are minimized analytics, not differentially private analytics.

**Federated learning:** independent synthetic client datasets train regression weights locally; each round aggregates sample-weighted model deltas with FedAvg. Local-only and centralized baseline models train alongside the federated model, evaluated on the same held-out synthetic distribution. Customer memory and conversations are never training data. See `backend/federation.py`.

Each model update is clipped to an L2 norm threshold, then receives independent Gaussian noise with standard deviation `noise_multiplier × clip`. The seeded RNG supports reproducible experiments; it is not a production privacy RNG. There is no privacy accountant or epsilon/delta claim. The `SecureAggregation` class is an extension interface whose implementation averages plaintext updates. It offers no cryptographic secure aggregation.

**Memory synchronization:** `POST /api/federation/sync` requires collection and federation consent, enabled source/destination policies, source ownership and matching version, and a recognized catalog category label. It copies only that label to a different node. Destination conflicts fail with 409 rather than silently overwriting. Brands, budgets, dislikes, and conversations are never shared. Raw requests and preference values are omitted from audit payloads.

Set `ADMIN_EMAIL` before registering the designated administrator account. `GET /api/admin/summary` and `PUT /api/admin/nodes` enforce admin role. The latter registers/updates the three allowlisted demo identities' sync policies with optimistic version checking. The prototype intentionally rejects arbitrary untrusted remote nodes.

## Deployment

Copy `.env.example` to `.env`, choose a strong `POSTGRES_PASSWORD`, and run `docker compose up --build`. Visit http://localhost:8080. PostgreSQL uses a named volume. The frontend proxies `/api` through nginx. The Python image runs as a non-root user.

`render.yaml` configures a Docker backend. Supply a PostgreSQL URL and frontend origin. On Render override the Docker command to respect the assigned port if needed: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.

For the complete Vercel deployment, use this repository's root directory. The root `vercel.json` builds React and packages its output in `public`; `app.py` serves the existing FastAPI backend under the same origin. Connect PostgreSQL through `DATABASE_URL` or `POSTGRES_URL`. The current production deployment uses a free-plan Neon database. See [DEPLOYMENT.md](DEPLOYMENT.md) for redeployment and live verification commands.

Do not expose this academic demonstration as a hardened production service without distributed rate limiting, database constraints and transactional concurrency hardening, physical node isolation, retention jobs, session cleanup, monitored migrations, and operational security review. The source intentionally makes no formal privacy guarantee. Semantic embeddings, payment processing, autonomous cart mutation, shipping/inventory management, and cryptographic secure aggregation are not implemented. Optional LLM requests disclose the current user request and selected catalog to the configured provider; keys stay server-side.

The supplied brief ended at “Federated Coordination Layer”; implementation follows the requirements available in that attachment.
