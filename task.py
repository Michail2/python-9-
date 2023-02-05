import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор и спрашивает пользователя об их поле."""
    reply_keyboard = [["Мужской", "Женский", "Другое"]]

    await update.message.reply_text(
        "Привет! Меня зовут профессор Бот. Я проведу с вами беседу. "
        "Отправить / отменить, чтобы перестать разговаривать со мной.\n\n"
        "Ты мальчик или девочка?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Мальчик или девочка?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет выбранный пол и запрашивает фотографию."""
    user = update.message.from_user
    logger.info("Пол %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Я вижу! Пожалуйста, пришлите мне свою фотографию, "
        "так что я знаю, как ты выглядишь, или отправляй / пропускай, если не хочешь.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет фотографию и запрашивает местоположение."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Фотография %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Великолепно! А теперь, пожалуйста, пришлите мне свое местоположение или отправьте / пропустите, если вы этого не хотите."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропускает фотографию и запрашивает местоположение."""
    user = update.message.from_user
    logger.info("Пользователь %s не отправлял фотографию.", user.first_name)
    await update.message.reply_text(
        "Держу пари, ты выглядишь великолепно! Теперь, пришлите мне, пожалуйста, ваше местоположение или отправьте /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет местоположение и запрашивает некоторую информацию о пользователе."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Местоположение %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Может быть, я смогу как-нибудь навестить тебя! По крайней мере, расскажи мне что-нибудь о себе."
    )

    return BIO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пропускает местоположение и запрашивает информацию о пользователе."""
    user = update.message.from_user
    logger.info("Пользователь %s не отправил местоположение.", user.first_name)
    await update.message.reply_text(
        "Ты кажешься немного параноиком! По крайней мере, расскажи мне что-нибудь о себе."
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет информацию о пользователе и завершает беседу."""
    user = update.message.from_user
    logger.info("Биография %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Спасибо! Я надеюсь, что когда-нибудь мы сможем поговорить снова.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет и завершает разговор."""
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    await update.message.reply_text(
        "Пока! Я надеюсь, что когда-нибудь мы сможем поговорить снова.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5756866745:AAG6HQxYu_P-5SWV0FBiXsSS7i7FgYK6rWQ").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()