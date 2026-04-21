"""Telegram bot application for handling user interactions."""

import logging

from src.db import user_service_context
from src.models.infisical import InfisicalSecretsKeys
from src.models.telegram_app_handlers import TelegramAppHandlers
from src.secrets import secrets_manager
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ExtBot

logger = logging.getLogger(__name__)

token = secrets_manager.get_secret(InfisicalSecretsKeys.TELEGRAM_ACCESS_TOKEN)

bot_commands = [
    BotCommand(TelegramAppHandlers.SUBSCRIBE, "Subscribe to the bot."),
    BotCommand(TelegramAppHandlers.UNSUBSCRIBE, "Unsubscribe from the bot."),
]


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /subscribe command."""
    logger.info(
        f"Received /subscribe command from user {update.effective_user.id if update.effective_user else 'unknown'}"
    )
    if not update.effective_user or not update.message:
        return

    chat_id = update.effective_user.id

    try:
        async with user_service_context() as user_service:
            logger.info(f"Checking subscription status for user {chat_id}...")
            user = await user_service.get_user(chat_id)

            if user.is_subscribed:
                logger.info(f"User {chat_id} is already subscribed.")
                await update.message.reply_text("You are already subscribed.")
                return

            user.is_subscribed = True
            await user_service.update_user(user)

            logger.info(f"User {chat_id} has been subscribed.")
            await update.message.reply_text("Welcome! You are now subscribed.")

    except ValueError:
        logger.warning(f"Unauthorized access attempt by user {chat_id}.")
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
    except Exception as e:
        logger.error(f"Error in subscribe command: {e}")
        await update.message.reply_text("An internal error occurred.")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /unsubscribe command."""
    logger.info(
        f"Received /unsubscribe command from user {update.effective_user.id if update.effective_user else 'unknown'}"
    )
    if not update.effective_user or not update.message:
        return

    chat_id = update.effective_user.id

    try:
        async with user_service_context() as user_service:
            logger.info(f"Checking subscription status for user {chat_id}...")
            user = await user_service.get_user(chat_id)

            if not user.is_subscribed:
                logger.info(f"User {chat_id} is not currently subscribed.")
                await update.message.reply_text("You are not currently subscribed.")
                return

            user.is_subscribed = False
            await user_service.update_user(user)

            logger.info(f"User {chat_id} has been unsubscribed.")
            await update.message.reply_text("You have been unsubscribed.")

    except ValueError:
        logger.warning(f"Unauthorized access attempt by user {chat_id}.")
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
    except Exception as e:
        logger.error(f"Error in unsubscribe command: {e}")
        await update.message.reply_text("An internal error occurred.")


async def post_init(application: Application) -> None:
    """Post-initialization setup."""
    bot: ExtBot = application.bot
    await bot.set_my_commands(bot_commands)


def start_telegram_application() -> None:
    """Start the application."""
    application = Application.builder().token(token).post_init(post_init).build()

    application.add_handler(CommandHandler(TelegramAppHandlers.SUBSCRIBE, subscribe))
    application.add_handler(CommandHandler(TelegramAppHandlers.UNSUBSCRIBE, unsubscribe))

    logger.info("Bot started and listening...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
