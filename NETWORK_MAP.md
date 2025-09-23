## GenX_FX Network Map

### Services (Docker Compose Production)
- api (`genx-api`): Node/Express server on port 8000. Provides `/api/*` and `/api/mt45/*` for EAs. Depends on Postgres, Mongo, Redis.
- postgres (`genx-postgres`): Postgres 15 on 5432. Stores core app data.
- mongo (`genx-mongo`): MongoDB 7 on 27017. Used by AI training/services.
- redis (`genx-redis`): Redis 7 on 6379 with password. Caching/queues.
- discord_bot: Connects to `api:8000` and Discord API.
- telegram_bot: Connects to `api:8000` and Telegram Bot API.
- websocket_feed: Connects to Postgres and Redis. Publishes feeds.
- scheduler: Connects to `api:8000` and Postgres.
- nginx: Public ingress on 80/443, reverse-proxy to `api:8000`.
- prometheus (9090), grafana (3000): monitoring.

### External Connections
- Broker APIs: Bybit (REST/WebSocket), FXCM/ForexConnect (if enabled), MT4/MT5 EAs via HTTP polling to `/api/mt45`.
- LLM: Gemini for analysis; minimize usage via batching and caching.
- Messaging: Discord, Telegram.

### Ports
- Public: 80, 443 (nginx); 8000 (api, if not proxied); 3000 (grafana); 9090 (prometheus). Databases should not be public.
- Internal: 5432 (postgres), 27017 (mongo), 6379 (redis).

### Data Flows
- EAs -> nginx/api: register/heartbeat -> api stores state (Redis/Postgres) -> signals queued -> EAs GET signals -> EA executes trade on broker.
- websocket_feed/scheduler -> databases and api.

### Cost-Saving
- CI/CD: GitHub Actions free tier.
- Registry: GHCR or Docker Hub free.
- LLM: Batch requests; cache per symbol/timeframe; set monthly caps.
- Monitoring: Prometheus/Grafana OSS.

### Potential Paid Services & Alternatives
- Cloud VMs: Prefer smallest free tier or spot/preemptible. Consider Fly.io or Railway free tiers for non-trading components.
- Managed DBs: Use single Postgres with nightly backups. For dev, SQLite.
- Secrets: GitHub Secrets; server-side `.env` with chmod 600.
