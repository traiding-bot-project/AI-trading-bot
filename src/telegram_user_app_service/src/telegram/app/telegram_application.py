"""Telegram bot application for handling user interactions."""

import logging

from market_intel_lib.db import subscription_token_service_context, user_service_context
from market_intel_lib.models.infisical import InfisicalSecretsKeys
from market_intel_lib.secrets import secrets_manager
from src.models.telegram_app_handlers import TelegramAppHandlers
from market_intel_lib.models.user import User
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ExtBot

logger = logging.getLogger(__name__)

token = secrets_manager.get_secret(InfisicalSecretsKeys.TELEGRAM_ACCESS_TOKEN)

bot_commands = [
    BotCommand(
        TelegramAppHandlers.SUBSCRIBE, "Subscribe to the bot with the access token."
    ),
    BotCommand(TelegramAppHandlers.UNSUBSCRIBE, "Unsubscribe from the bot."),
]


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /subscribe command."""
    logger.info(
        f"Received /subscribe command from user {update.effective_user.id if update.effective_user else 'unknown'}"
    )
    if not update.effective_user or not update.message:
        return

    tg_user = update.effective_user
    token_value = context.args[0] if context.args and len(context.args) > 0 else None

    if not token_value:
        await update.message.reply_text(
            "To subscribe, please provide a valid subscription token. Use /subscribe <token> to subscribe."
        )
        return

    try:
        async with (
            user_service_context() as user_service,
            subscription_token_service_context() as token_service,
        ):
            logger.info(f"Validating subscription token for user {tg_user.id}...")
            await token_service.validate_token(token_value)

            try:
                user = await user_service.get_user(tg_user.id)
            except ValueError:
                user = None

            if user and user.is_subscribed:
                logger.info(f"User {tg_user.id} is already subscribed.")
                await update.message.reply_text("You are already subscribed.")
                return

            if not user:
                user = User(
                    first_name=tg_user.first_name or "",
                    last_name=tg_user.last_name or "",
                    username=tg_user.username or f"user_{tg_user.id}",
                    chat_id=tg_user.id,
                    is_subscribed=True,
                )
                user = await user_service.register_user(user)
            else:
                user.is_subscribed = True
                user = await user_service.update_user(user)

            await token_service.activate_token(token_value, user)
            logger.info(f"User {tg_user.id} subscribed successfully with token.")
            await update.message.reply_text("Welcome! You are now subscribed.")
            return

    except ValueError as e:
        if token_value:
            logger.warning(
                f"Invalid or expired token attempt by user {tg_user.id}: {e}"
            )
            await update.message.reply_text(
                "Invalid or expired subscription token. Please request a new one."
            )
        else:
            logger.warning(f"Unauthorized access attempt by user {tg_user.id}.")
            await update.message.reply_text(
                "Sorry, you are not authorized to use this bot."
            )
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

    tg_user = update.effective_user

    try:
        async with user_service_context() as user_service:
            logger.info(f"Checking subscription status for user {tg_user.id}...")
            user = await user_service.get_user(tg_user.id)

            if not user.is_subscribed:
                logger.info(f"User {tg_user.id} is not currently subscribed.")
                await update.message.reply_text("You are not currently subscribed.")
                return

            user.is_subscribed = False
            await user_service.update_user(user)

            logger.info(f"User {tg_user.id} has been unsubscribed.")
            await update.message.reply_text("You have been unsubscribed.")

    except ValueError:
        logger.warning(f"Unauthorized access attempt by user {tg_user.id}.")
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot."
        )
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
    application.add_handler(
        CommandHandler(TelegramAppHandlers.UNSUBSCRIBE, unsubscribe)
    )

    logger.info("Bot started and listening...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
