# Telegram Bot Horizontal Scaling with Docker Compose

This project demonstrates how to horizontally scale Telegram bots using **Python**, **Flask**, **python-telegram-bot**, and **HAProxy**.  All orchestrated with **Docker Compose**.

> **Note**: Features like `ConversationHandlers` do not function properly without third-party state management tools such as Redis or RabbitMQ. This is because each bot instance maintains its own memory, and updates are distributed to different instances based on HAProxy's load balancing strategy (e.g., round-robin, random).

## Features
- **Horizontal Scaling**: Multiple bot instances (master and slaves) handle updates concurrently.
- **Webhook Management**: Each bot instance registers a webhook to receive updates from Telegram.
- **Health Check**: Each bot exposes a `/healthcheck` endpoint to verify its status.
- **Load Balancing**: HAProxy distributes incoming requests across multiple bot instances.
- **Dockerized Setup**: Easy deployment with Docker and Docker Compose.

---

## Prerequisites
- **Docker** and **Docker Compose** installed.
- A valid Telegram bot token. Obtain one from [BotFather](https://core.telegram.org/bots).
- A valid domain & certificate - [Certificate where do I get one and how](https://core.telegram.org/bots/webhooks#a-certificate-where-do-i-get-one-and-how)
- Default port used is 3000, this can be changed in [docker-compose.yml](./docker-compose.yml) under `Services -> HAProxy -> Ports` 
---

## Setup and Usage

### 1. Clone the Repository
```bash
git clone https://github.com/TropicalShadow/scaling-telegram-bot.git
cd scaling-telegram-bot
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Or create a new `.env` file with the following content:
```env
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_CALLBACK_SECRET=<your-secret-token>
WEBHOOK_URL=<your-public-webhook-url>
WEBHOOK_PORT=3000
```

Replace:
- `<your-telegram-bot-token>` with your bot's token.
- `<your-secret-token>` with a secure secret token (this can be anything, just to secure the webhooks to telegram).
- `<your-public-webhook-url>` with your server's public URL (e.g., `https://example.com`).
- WEBHOOK_PORT is default to 3000, this is for internal use by HA-proxy and docker. Correlation to [Dockerfile](./Dockerfile) `EXPOSE 3000`

### 3. Configure HAProxy
Edit `haproxy.cfg` if needed. The default configuration routes all requests to bot instances:
```haproxy
defaults
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http-in
    bind *:80
    default_backend bots

backend bots
    balance roundrobin
    server master-app master-app:3000 check
    server slave-app slave-app:3000 check
```

### 4. Build and Run
Run the project with Docker Compose:
```bash
docker-compose up --build
```

This will:
- Start an HAProxy instance.
- Start a master bot instance.
- Start a slave bot instance.

---

## How It Works

### Bot Instances
- **Master Instance**: Handles webhook registration with Telegram and processes updates.
- **Slave Instances**: Only process updates routed by HAProxy.

### Load Balancing
- HAProxy routes incoming webhook requests to available bot instances using round-robin scheduling.
- Each bot instance runs independently, ensuring scalability.

### Health Check
- Each bot instance exposes a `/healthcheck` endpoint at `<WEBHOOK_URL>/healthcheck`.

Example:
```bash
curl http://localhost:3000/healthcheck
# Output: "The bot is still running fine :) - from master-app"
```

---

## Project Structure
```plaintext
├── Dockerfile          # Dockerfile for bot instances
├── docker-compose.yml  # Docker Compose setup
├── haproxy.cfg         # HAProxy configuration
├── app/
│   ├── main.py         # Bot application
│   ├── requirements.txt # Python dependencies
└── .env                # Environment variables
```

---

## Extending the Project
- Add more slave instances in `docker-compose.yml` for higher concurrency.
- Enhance HAProxy with additional routing logic.
- Deploy the setup on Kubernetes for production-scale workloads.

---

## Acknowledgements
- **[python-telegram-bot](https://python-telegram-bot.org/)** for the Telegram Bot API wrapper.
- **[Flask](https://flask.palletsprojects.com/)** for handling webhooks.
- **[HAProxy](http://www.haproxy.org/)** for load balancing.

---

Feel free to contribute and make this project even better! 🚀

--- 