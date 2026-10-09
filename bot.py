
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


@bot.message_handler(commands=["thimbles"])
def thimbles(message):
    bot.reply_to(
        message,
        "🥤 RICHE BABE - THIMBLES \n\n"
        "🎯 Si 3 gobelets sont proposés et qu'une seule boule est cachée :\n"
        "• Chance théorique au hasard : 1 sur 3 (33,3 %).\n\n"
        "⚠️ RISQUES :\n"
        "• Les mélanges rapides rendent le suivi incertain.\n"
        "• Aucune méthode ne garantit de trouver la boule.\n"
        "• Ne mise que ce que tu peux te permettre de perdre.\n\n"
        "💡 Riche Babe ne peut pas prédire la position réelle de la boule."
    )

bot.infinity_polling()
