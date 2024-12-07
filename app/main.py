#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from http import HTTPStatus
from dotenv import load_dotenv
import sys
import os

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, Response, make_response, request

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        f"Hello! I am a bot running on the server with the ID <code>{APP_ID}</code>.\n\n"
        f"To check if the bot is still running, call <code>{WEBHOOK_URL}/healthcheck</code>.\n\n"
    )

    await update.message.reply_html(text=text)


async def main() -> None:
    application = (
        Application.builder().token(TELEGRAM_BOT_TOKEN).concurrent_updates(True).updater(None).build()
    )        

    application.add_handler(CommandHandler("start", start))

    await run_webhook_stuff(application)


async def run_webhook_stuff(application: Application):

    if IS_MASTER:
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram", allowed_updates=Update.ALL_TYPES, secret_token=TELEGRAM_CALLBACK_SECRET)

    flask_app = Flask(__name__)

    @flask_app.route("/")
    @flask_app.route("/healthcheck")
    async def index() -> Response:
        response = make_response(f"The bot is still running fine :) - from {APP_ID}", HTTPStatus.OK)
        response.mimetype = "text/plain"
        return response

    @flask_app.post("/telegram")
    async def telegram() -> Response:
        api_secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if api_secret_token != TELEGRAM_CALLBACK_SECRET:
            return Response(status=HTTPStatus.FORBIDDEN)

        await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
        return Response(status=HTTPStatus.OK)


    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(flask_app),
            port=WEBHOOK_PORT,
            use_colors=False,
            host="0.0.0.0",
        )
    )

    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()



if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT") or 3000)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CALLBACK_SECRET = os.getenv("TELEGRAM_CALLBACK_SECRET")

    if not WEBHOOK_URL or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CALLBACK_SECRET:
        logger.error("Please set the WEBHOOK_URL, TELEGRAM_BOT_TOKEN and TELEGRAM_CALLBACK_SECRET environment variables.")
        sys.exit(1)

    APP_ID = os.getenv("APP_ID") or "Invalid App ID"
    IS_MASTER = "--master" in sys.argv

    asyncio.run(main())