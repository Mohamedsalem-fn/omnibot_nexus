import os
import logging
import asyncio
import threading
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

from flask import Flask, jsonify, request
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message

# --- Configuration & Logging ---

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("OmniBotNexus")

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))
DB_PATH = os.getenv("DB_PATH", "data/nexus.db")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set in environment variables.")
    exit(1)

# --- Database Layer ---

class Database:
    """Handles SQLite persistence for tasks and logs."""
    
    def __init__(self):
        self.conn = None
        self.lock = threading.Lock()

    def connect(self):
        if not self.conn:
            # Ensure directory exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return self.conn

    def init_db(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT,
                payload TEXT,
                status TEXT,
                created_at TIMESTAMP,
                executed_at TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database initialized.")

    def log_task(self, task_type: str, payload: dict, status: str):
        conn = self.connect()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO tasks (task_type, payload, status, created_at) VALUES (?, ?, ?, ?)",
            (task_type, json.dumps(payload), status, now)
        )
        conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

# --- Task Orchestration Engine ---

class TaskOrchestrator:
    """Manages background asynchronous tasks."""

    def __init__(self, db: Database, bot: Bot):
        self.db = db
        self.bot = bot
        self.is_running = False

    async def process_task(self, task_type: str, payload: dict):
        logger.info(f"Processing task: {task_type} with payload: {payload}")
        await asyncio.sleep(1)  # Simulate work
        
        # Example: Notify admin on completion
        # await self.bot.send_message(chat_id=os.getenv("ADMIN_CHAT_ID"), text=f"Task {task_type} completed.")
        
        self.db.log_task(task_type, payload, "completed")

    async def background_worker(self):
        while self.is_running:
            logger.debug("Orchestrator heartbeat...")
            await asyncio.sleep(10)

    def start(self):
        self.is_running = True
        logger.info("Task Orchestrator started.")

    def stop(self):
        self.is_running = False
        logger.info("Task Orchestrator stopped.")

# --- Web API (Flask) ---

def create_flask_app(db: Database, orchestrator: TaskOrchestrator):
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "OmniBot Nexus", "timestamp": datetime.now().isoformat()})

    @app.route("/status", methods=["GET"])
    def status():
        return jsonify({"database_stats": db.get_stats(), "orchestrator_running": orchestrator.is_running})

    @app.route("/trigger", methods=["POST"])
    def trigger_task():
        data = request.json
        if not data or "task_type" not in data:
            return jsonify({"error": "Missing task_type"}), 400
        
        # Schedule task (In a real app, use a Queue)
        asyncio.create_task(orchestrator.process_task(data["task_type"], data))
        return jsonify({"message": "Task queued"}), 202

    return app

# --- Telegram Bot (Aiogram) ---

def setup_telegram_bot(dp: Dispatcher, orchestrator: TaskOrchestrator):
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer("Welcome to OmniBot Nexus. System operational.")

    @router.message(Command("status"))
    async def cmd_status(message: Message):
        await message.answer(f"Orchestrator Status: {'Running' if orchestrator.is_running else 'Stopped'}")

    @router.message()
    async def echo(message: Message):
        logger.info(f"Received message: {message.text}")
        # Trigger a task based on message
        await orchestrator.process_task("echo_task", {"text": message.text})

    dp.include_router(router)

# --- Main Entry Point ---

async def main():
    # Initialize Components
    db = Database()
    db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    orchestrator = TaskOrchestrator(db, bot)

    # Setup Telegram
    setup_telegram_bot(dp, orchestrator)

    # Setup Flask (Run in separate thread)
    flask_app = create_flask_app(db, orchestrator)
    
    def run_flask():
        logger.info(f"Starting Flask Web Server on port {WEB_PORT}")
        # Use simple server for demo, production should use Gunicorn/Uvicorn
        flask_app.run(host="0.0.0.0", port=WEB_PORT, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Orchestrator
    orchestrator.start()
    
    # Start Telegram Polling
    logger.info("Starting Telegram Bot Polling...")
    try:
        await dp.start_polling(bot)
    finally:
        orchestrator.stop()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")