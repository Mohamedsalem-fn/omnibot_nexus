# 🚀 OmniBot Nexus

<div align="center">

**The Future of Multi-Platform Automation**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightblue.svg)](https://www.docker.com/)

</div>

---

## 📖 Overview

**OmniBot Nexus** is an enterprise-grade automation hub designed to orchestrate complex workflows across Telegram, WhatsApp, and Web APIs. Built with a focus on scalability, reliability, and real-time monitoring, it serves as the central nervous system for your digital operations.

### 🌟 Key Features

- **🤖 Multi-Platform Support:** Native integration with Telegram (via Aiogram) and extensible architecture for WhatsApp.
- **⚡ Task Orchestration:** Advanced background job scheduling and execution engine.
- **📊 Real-Time Monitoring:** Flask-based Web API for health checks, status metrics, and manual triggering.
- **🛡️ Production Ready:** Comprehensive error handling, structured logging, and Docker containerization.
- **💾 Persistent Storage:** SQLite database for state management and task history.

---

## 🏗️ Architecture

The system is built on a modular asynchronous architecture:

1.  **Core Loop:** An `asyncio` event loop managing the Telegram bot polling and background task scheduler.
2.  **Web Interface:** A synchronous Flask server running in a separate thread to serve API requests without blocking the bot.
3.  **Data Layer:** SQLite with ORM-like abstraction for configuration and logs.

---

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- Docker (optional, but recommended)
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/your-org/omnibot-nexus.git
cd omnibot-nexus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and tokens

# Initialize Database
python -c "from main import Database; Database().init_db()"

# Run
python main.py
```

### Docker Deployment

```bash
# Build the image
docker build -t omnibot-nexus .

# Run the container
docker run -d \
  --name omnibot \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  omnibot-nexus
```

---

## 📚 Usage

### Telegram Bot

Once running, interact with the bot on Telegram. Start commands trigger the orchestration engine.

### Web API

The Flask server exposes the following endpoints:

- `GET /health`: Returns system health and uptime.
- `GET /status`: Returns current task queue status.
- `POST /trigger`: Manually triggers a specific task payload.

---

## 🧪 Testing

Run the test suite using pytest:

```bash
pytest tests/
```

---

## 📝 Contributing

We welcome contributions! Please ensure all code passes the linting and testing stages before submitting a PR.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>Built with ❤️ by the OmniBot Team</b>
</div>