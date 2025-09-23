[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Mouy-leng/GenX_FX)

# 🚀 GenX FX Trading Platform

Advanced AI-powered trading system with real-time services, unified CLIs, API endpoints, MT4/MT5 Expert Advisors, and multi-cloud deployment.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Node](https://img.shields.io/badge/Node-18%2B-green.svg)](https://nodejs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

GenX FX brings together a Python FastAPI backend, a TypeScript/Express+Vite service layer, optional React client, unified Python and Node CLIs, and MT4/MT5 Expert Advisors. It supports local development, containerized deployment, and cloud automation (AWS/VPS).

## ✨ Key Features

- 🤖 AI & Signals: Ensemble models and technical indicators (Python)
- 📊 API Services: FastAPI (`api/`) and WebSocket/Express server (`services/server/`)
- 💬 Unified CLIs: `head_cli.py`, `genx_unified_cli.py`, `genx_master_cli.py`, and `genx-cli` (Node)
- 🔗 Broker/EA Integration: MT4/MT5 Expert Advisors and CSV/Excel signals
- ☁️ Deployment: Docker Compose, AWS free/full, VPS scripts
- 🧪 Testing: Python tests and Vitest for TypeScript services

## 🏗️ Architecture

```
GenX FX Platform
├── 🧠 Core & AI (Python): core/, ai_models/
├── 📡 API (Python): api/
├── 🌐 Services (Node): services/server/ (Express + WebSocket + Vite)
├── 🖥️ Client (React/Vite): client/
├── 🛠️ CLIs: head_cli.py, genx_unified_cli.py, genx_master_cli.py, genx-cli/
├── 📈 Expert Advisors: expert-advisors/ (MT4/MT5)
├── 🚀 Deployment: deploy/, docker-compose*.yml, Dockerfile*
└── ⚙️ Config & Scripts: config/, scripts/, .env.example
```

## 📂 Project Structure (root-level highlights)

- `api/` FastAPI app and utilities
  - `main.py` API entry (default dev port 8000)
- `services/server/` Node/Express server with WebSocket and Vite integration
  - `index.ts` Server entry (default port 5000)
- `client/` Vite + React client (dev port 5173)
- `core/` Trading engine, indicators, risk management, strategies
- `ai_models/` ML models and utilities
- `expert-advisors/` MT4/MT5 EAs and examples
- `signal_output/` Generated signals: CSV, JSON, Excel
- `genx-cli/` Node-based plugin CLI (`npx genx-cli`)
- `head_cli.py` Unified head CLI for AMP and GenX
- `genx_unified_cli.py` Unified CLI including setup/deploy/monitor
- `genx_master_cli.py` Master CLI wrapping all CLIs
- `deploy/`, `docker-compose*.yml`, `Dockerfile*` Deployment assets
- `scripts/` Supporting Python/shell scripts
- `.env.example` Environment template

For a deeper tree and component mapping, see `PROJECT_STRUCTURE.md` and `FOLDER_STRUCTURE.md`.

## 🚀 Quick Start (Local Dev)

### 1) Prerequisites
- Python 3.8+
- Node 18+
- pip and npm
- Optional: Docker

### 2) Install dependencies
```bash
# Python deps
pip install -r requirements.txt

# Node deps
npm install
```

### 2.5) Configure environment
Copy `.env.example` to `.env` and fill in required values (API keys, ports, database, etc.).
```bash
cp .env.example .env
# then edit .env
```

### 3) Start everything (client + server + API)
```bash
npm run dev
# Starts:
# - Client (Vite):        http://0.0.0.0:5173
# - Node/Express server:  http://0.0.0.0:5000 (with WebSocket)
# - FastAPI:              http://0.0.0.0:8000
```

### 4) Start services individually (optional)
```bash
# API only (FastAPI)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Server only (Express/WebSocket/Vite middleware)
npm run server

# Client only (Vite)
npm run client
```

## 🎮 Unified CLI Usage (Python)

```bash
# Head CLI (recommended)
python3 head_cli.py overview
python3 head_cli.py help-all
python3 head_cli.py status
python3 head_cli.py genx status
python3 head_cli.py amp auth --status

# Unified CLI (setup/deploy/monitor)
python3 genx_unified_cli.py status
python3 genx_unified_cli.py setup local
python3 genx_unified_cli.py deploy aws-free --yes

# Master CLI (wraps all)
python3 genx_master_cli.py overview
python3 genx_master_cli.py quick_status
```

## 🧰 Node CLI Usage (`genx-cli`)

```bash
# List plugins
npx genx-cli --list-plugins

# Run a plugin
npx genx-cli --run-plugin license_checker

# Run a configured command from .julenrc
npx genx-cli run <command-name>
```

## 📡 API Endpoints (FastAPI)

Default dev host/port: `http://0.0.0.0:8000`

- `GET /` Basic info
- `GET /health` Health check (DB probe)
- `GET /trading-pairs` Active trading pairs (SQLite)
- `GET /users` Users list (SQLite)
- `GET /mt5-info` MT5 configuration info

## 🔌 WebSocket & Server (Node/Express)

- Server: `services/server/index.ts` (default port 5000)
- Health: `GET /health`
- WebSocket: echo and welcome events on connect
- Dev mode serves Vite middleware; production serves static built assets

## 📈 Signals & EAs

- Generated files in `signal_output/`:
  - `MT4_Signals.csv`, `MT5_Signals.csv`, `genx_signals.xlsx`, `genx_signals.json`
- Expert Advisors in `expert-advisors/` (MT4/MT5 examples and advanced EAs)
- See `EA_SETUP_GUIDE.md`, `GOLD_MASTER_EA_GUIDE.md`, `EA_EXPLAINED_FOR_BEGINNERS.md`

## ⚙️ Configuration

- Copy `.env.example` to `.env` and fill values as needed
- Trading config templates in `config/`
- API keys and secrets setup: `API_KEY_SETUP.md`, `COMPLETE_GITHUB_SECRETS_SETUP.md`

## 🛠️ Scripts & Management

- Start/Stop/Status scripts: `start_trading.sh`, `stop_trading.sh`, `status.sh`
- Data, training, and integration utilities: `scripts/` and `core/`
- Validation and setup helpers: `verify_docker_setup.py`, `setup_aws_deployment.sh`, `setup_forexconnect.sh`

## ☁️ Deployment

- Docker (local):
  ```bash
  docker-compose up -d
  ```
- AWS (free tier/full): see `deploy/` and run via unified CLI:
  ```bash
  python3 genx_unified_cli.py deploy aws-free --yes
  ```
- Additional guides: `DEPLOYMENT.md`, `DOCKER_DEPLOYMENT_SUMMARY.md`, `AWS_DEPLOYMENT_GUIDE.md`, `deploy/*`

## 🧪 Testing

```bash
# Python tests
python -m pytest -q

# TypeScript/Vitest
npm test
```

## 📚 More Documentation

- `GETTING_STARTED.md` Quick demo and Excel/CSV usage
- `PROJECT_STRUCTURE.md` Complete project structure and mapping
- `SYSTEM_ARCHITECTURE_GUIDE.md` Architecture details
- `INTEGRATION_GUIDE.md` Integration references

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m "feat: add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See `LICENSE`.

## 🔗 Links

- Repository: https://github.com/Mouy-leng/GenX_FX
- Issues: https://github.com/Mouy-leng/GenX_FX/issues
- Discussions: https://github.com/Mouy-leng/GenX_FX/discussions
