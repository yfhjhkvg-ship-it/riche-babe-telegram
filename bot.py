
import os
import telebot

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Le jeton Telegram est manquant.")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Bienvenue chez Riche Babe ! 👑\n\n"
        "Ton bot est en ligne.\n"
        "Tape /help pour voir les commandes."
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "Commandes disponibles :\n"
        "/start - Démarrer le bot\n"
        "/help - Afficher l'aide"
    )

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, "👑 Riche Babe te répond !")

bot.infinity_polling()
