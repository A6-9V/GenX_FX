[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Mouy-leng/GenX_FX)

# 🚀 GenX Trading Platform

**Advanced AI-Powered Forex & Cryptocurrency Trading System**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

GenX Trading Platform is a comprehensive AI-powered trading system that combines machine learning, real-time market analysis, and automated execution capabilities. The platform features a unified CLI interface, advanced signal generation, and multi-broker integration.

## ✨ Key Features

- 🤖 **AMP (Automated Model Pipeline)** - AI trading models with sentiment analysis
- 📊 **Real-time Market Analysis** - Multi-source data aggregation and processing
- 💬 **Interactive AI Chat** - Communicate with the trading system in natural language
- 🔗 **Multi-Broker Integration** - ForexConnect, FXCM, Exness support
- 📈 **Advanced Signal Generation** - ML-based trading signals with Excel integration
- 🌐 **Cloud Deployment** - AWS, Heroku, Google Cloud ready
- 🎮 **Unified CLI** - Single command interface for all operations

## 🏗️ Architecture

```
GenX Trading Platform
├── 🎯 Head CLI (./genx) - Unified command center
├── 🤖 AMP System - AI models & authentication
├── ⚙️ GenX Core - Trading engine & signals
├── 💬 Chat Interface - Interactive AI communication
├── 📊 API Services - REST API & WebSocket feeds
├── 📈 Expert Advisors - MT4/MT5 integration
└── ☁️ Deployment - Multi-cloud support
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Mouy-leng/GenX_FX.git
cd GenX_FX

# Install dependencies
pip3 install --break-system-packages typer rich requests pyyaml python-dotenv

# Make CLI executable
chmod +x genx
```

### 2. System Overview
```bash
# Check system status
./genx overview

# View complete help
./genx help-all
```

### 3. Authentication
```bash
# Login to AMP system
./genx auth --action login --token YOUR_AMP_TOKEN

# Check authentication status
./genx auth
```

### 4. Start Trading
```bash
# Initialize the system
./genx init

# Check system status
./genx status

# Start interactive chat with AI
./genx chat
```

## 📂 Project Structure

```
GenX_FX/
├── 🎮 CLI Tools
│   ├── head_cli.py          # Unified command interface
│   ├── amp_cli.py           # AMP system management
│   ├── genx_cli.py          # GenX core management
│   └── genx                 # Launcher script
│
├── 🤖 AMP System
│   ├── amp_auth.py          # Authentication management
│   ├── amp_client.py        # API client
│   ├── simple_amp_chat.py   # Interactive chat
│   └── amp-plugins/         # AMP plugins
│
├── 🧠 AI Models
│   ├── ai_models/           # ML models and predictors
│   ├── ensemble_model.py    # Ensemble trading models
│   └── market_predictor.py  # Market prediction engine
│
├── ⚙️ Core Trading Engine
│   ├── core/                # Trading strategies and patterns
│   ├── signal_validators/   # Signal validation logic
│   └── trading_engine.py    # Main trading engine
│
├── 📊 API & Services
│   ├── api/                 # FastAPI REST services
│   ├── services/            # Background services
│   └── websocket_service.py # Real-time data feeds
│
├── 📈 Expert Advisors
│   ├── expert-advisors/     # MT4/MT5 EAs
│   ├── GenX_AI_EA.mq5      # AI-powered EA
│   └── GenX_Gold_Master_EA.mq4
│
├── ☁️ Deployment
│   ├── deploy/              # Deployment scripts
│   ├── docker-compose.yml   # Docker configuration
│   └── aws/                 # AWS deployment files
│
└── 📋 Configuration
    ├── config/              # Trading configurations
    ├── .env.example         # Environment template
    └── requirements.txt     # Python dependencies
```

## 🎮 CLI Commands

### System Management
```bash
./genx overview              # System overview
./genx status               # Complete system status
./genx init                 # Initialize system
./genx tree                 # Project structure
```

### AMP (AI System)
```bash
./genx amp status           # AMP system status
./genx amp auth --status    # Check authentication
./genx amp monitor --status # Performance monitoring
./genx amp deploy           # Deploy to production
```

### Trading Operations
```bash
./genx genx status          # Trading system status
./genx genx excel           # Excel signal management
./genx genx forexconnect    # ForexConnect operations
./genx genx config          # Configure API keys
```

### Communication
```bash
./genx chat                 # Interactive AI chat
./genx logs                 # View system logs
./genx monitor              # Performance monitoring
```

## 🤖 AMP System Features

The **Automated Model Pipeline (AMP)** is the AI brain of the platform:

- **Multi-Source Analysis**: News, Reddit, technical indicators
- **Real-time Predictions**: Market direction and price targets
- **Sentiment Analysis**: Social media and news sentiment
- **Adaptive Learning**: Continuous model improvement
- **Risk Management**: Automated stop-loss and take-profit

### AMP Chat Examples
```bash
./genx chat
You: What's the Bitcoin outlook?
AMP: Bitcoin shows bullish sentiment (68% positive mentions on Reddit).
     Technical indicators suggest upward momentum. Target: $48,000-$52,000

You: Give me trading signals
AMP: 🟢 BTC/USDT: LONG - Entry: $45,200, Stop: $43,800, Target: $48,500
     🟡 ETH/USDT: WAIT - Waiting for breakout confirmation
```

## 🔗 Broker Integration

### Supported Brokers
- **FXCM** - Full API integration with ForexConnect
- **Exness** - VPS deployment and MT4/MT5 EAs
- **Interactive Brokers** - API integration (planned)
- **Binance** - Cryptocurrency trading (planned)

### ForexConnect Setup
```bash
./genx genx forexconnect    # Setup and test ForexConnect
```

## 📊 Signal Generation

The platform generates trading signals through:

1. **AI Model Ensemble** - Multiple ML models combined
2. **Technical Analysis** - 50+ technical indicators
3. **Sentiment Analysis** - News and social media sentiment
4. **Risk Assessment** - Automated risk scoring

### Excel Integration
```bash
./genx genx excel           # Generate Excel reports
```

## ☁️ Deployment Options

### Docker Deployment
```bash
docker-compose up -d        # Local deployment
```

### AWS Deployment
```bash
./genx amp deploy           # Deploy to AWS
```

### Heroku Deployment
```bash
# See deploy/HEROKU_DEPLOYMENT_GUIDE.md
```

## 📈 Performance Monitoring

Monitor your trading system:

```bash
./genx monitor              # Real-time monitoring
./genx logs                 # System logs
./genx amp monitor --dashboard  # Advanced dashboard
```

## 🛡️ Security & Authentication

- **Token-based Authentication** - Secure AMP access
- **API Key Management** - Encrypted broker credentials
- **Environment Variables** - Secure configuration
- **Access Control** - Role-based permissions

## 🧪 Testing & Development

```bash
./genx amp test             # Run AMP tests
./genx amp verify           # Verify installation
./genx genx logs            # Debug logs
```

## 📚 Documentation

- [Head CLI Guide](HEAD_CLI_README.md) - Complete CLI documentation
- [AMP System Guide](amp-plugins/) - AI system documentation
- [Deployment Guides](deploy/) - Cloud deployment instructions
- [API Documentation](api/) - REST API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/Mouy-leng/GenX_FX
- **Issues**: https://github.com/Mouy-leng/GenX_FX/issues
- **Discussions**: https://github.com/Mouy-leng/GenX_FX/discussions

## 🆘 Support

- Use `./genx help-all` for complete command reference
- Check system status with `./genx overview`
- View logs with `./genx logs`
- Start interactive chat with `./genx chat`

---

**🚀 Ready to revolutionize your trading with AI?**

Start with `./genx overview` and explore the platform's capabilities!

# Docker Jules Orchestrator

[![Security](https://github.com/Mouy-leng/docker_jules_orchestrator/workflows/Enhanced%20Security%20Analysis/badge.svg)](https://github.com/Mouy-leng/docker_jules_orchestrator/actions/workflows/security-enhanced.yml)
[![Tests](https://github.com/Mouy-leng/docker_jules_orchestrator/workflows/Run%20Tests%20and%20Quality%20Checks/badge.svg)](https://github.com/Mouy-leng/docker_jules_orchestrator/actions/workflows/test.yml)
[![Code Quality](https://github.com/Mouy-leng/docker_jules_orchestrator/workflows/Code%20Quality%20Check/badge.svg)](https://github.com/Mouy-leng/docker_jules_orchestrator/actions/workflows/code-quality.yml)
[![Docker Build](https://github.com/Mouy-leng/docker_jules_orchestrator/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/Mouy-leng/docker_jules_orchestrator/actions/workflows/docker-build.yml)
[![Dependabot](https://img.shields.io/badge/dependabot-enabled-brightgreen.svg)](https://dependabot.com/)
[![Security Policy](https://img.shields.io/badge/security-policy-brightgreen.svg)](SECURITY.md)

## 🛡️ Security & Quality Status

This repository maintains high security standards through automated checks:

- **🔒 Security Analysis**: CodeQL, secret scanning, dependency vulnerability checks
- **🧪 Automated Testing**: Multi-Python version testing with coverage reporting
- **📊 Code Quality**: Linting, formatting, and type checking
- **🐳 Docker Security**: Container vulnerability scanning and build verification
- **🔄 Dependency Updates**: Automated security updates via Dependabot

## 🚀 Quick Start

[Your existing quick start content here...]

## 🔐 Security Features

- **Branch Protection**: Main branch requires passing security checks
- **Automated Scanning**: Weekly security audits and vulnerability detection
- **Secret Detection**: Prevents accidental credential exposure
- **Container Security**: Docker image vulnerability scanning
- **Dependency Monitoring**: Automatic security update notifications

## 📋 Requirements

[Your existing requirements content here...]

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run security checks
bandit -r .
safety check
```

## 🐳 Docker

[Your existing Docker content here...]

## 🔧 Development

[Your existing development content here...]

## 📚 Documentation

[Your existing documentation content here...]

## 🤝 Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Security Policy](SECURITY.md) before submitting changes.

## 📄 License

[Your existing license content here...]

---

**🔒 Security is our top priority. Report vulnerabilities privately following our [Security Policy](SECURITY.md).**
