

import os
import io
import cv2
import base64
import tempfile
import telebot
from openai import OpenAI

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise RuntimeError("Variable TELEGRAM_BOT_TOKEN manquante.")

if not OPENAI_API_KEY:
    raise RuntimeError("Variable OPENAI_API_KEY manquante.")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👑 Bienvenue chez Riche Babe !\n\n"
        "Envoie une photo ou une vidéo du jeu Thimbles.\n"
        "Je vais examiner les images pour tenter de "
        "localiser la boule.\n\n"
        "⚠️ La position ne peut pas être garantie "
        "si la boule est cachée."
    )


@bot.message_handler(commands=["help", "thimbles"])
def help_command(message):
    bot.reply_to(
        message,
        "🥤 RICHE BABE - THIMBLES\n\n"
        "Envoie une photo ou une vidéo claire du jeu.\n"
        "Je vais analyser les images disponibles.\n"
        "Je signalerai si la position est incertaine."
    )


def inspect_image(image_bytes):
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "Analyse cette image d'un jeu de gobelets. "
                        "Dis uniquement ce qui est visuellement "
                        "justifié. Si la boule est visible, indique "
                        "sa position et le gobelet correspondant "
                        "(gauche, milieu ou droite). Si elle est "
                        "cachée ou impossible à identifier, dis-le "
                        "clairement. Ne devine pas sa position."
                    )
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{encoded}"
                }
            ]
        }]
    )

    return response.output_text


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    status = bot.reply_to(message, "🔎 Analyse de la photo...")

    try:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        image_bytes = bot.download_file(file_info.file_path)

        result = inspect_image(image_bytes)

        bot.edit_message_text(
            "👑 RICHE BABE — Analyse\n\n" + result,
            message.chat.id,
            status.message_id
        )
    except Exception as exc:
        print("Erreur analyse photo:", exc)
        bot.reply_to(
            message,
            "❌ Analyse impossible. Vérifie la clé API "
            "et réessaie avec une image plus claire."
        )


@bot.message_handler(content_types=["video", "document"])
def handle_video(message):
    media = message.video or message.document

    if not media:
        return

    if message.document and not (
        media.mime_type or ""
    ).startswith("video/"):
        bot.reply_to(message, "Envoie un fichier vidéo valide.")
        return

    if media.file_size and media.file_size > 20 * 1024 * 1024:
        bot.reply_to(
            message,
            "Vidéo trop volumineuse pour cette version. "
            "Envoie une vidéo de moins de 20 Mo."
        )
        return

    status = bot.reply_to(
        message,
        "🎥 Réception de la vidéo. Extraction des images..."
    )

    path = None

    try:
        info = bot.get_file(media.file_id)
        data = bot.download_file(info.file_path)

        with tempfile.NamedTemporaryFile(
            suffix=".mp4", delete=False
        ) as temp:
            temp.write(data)
            path = temp.name

        cap = cv2.VideoCapture(path)

        if not cap.isOpened():
            raise RuntimeError("Vidéo illisible.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 1
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total / fps if fps else 0

        if total <= 0:
            raise RuntimeError("Aucune image trouvée.")

        # Examiner au maximum 8 images réparties dans la vidéo.
        count = min(8, max(1, int(duration) + 1))
        times = [
            duration * i / max(1, count - 1)
            for i in range(count)
        ]

        results = []

        for second in times:
            cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
            ok, frame = cap.read()

            if not ok:
                continue

            height, width = frame.shape[:2]
            scale = min(1, 900 / max(width, height))

            if scale < 1:
                frame = cv2.resize(
                    frame, (int(width * scale), int(height * scale))
                )

            ok, encoded = cv2.imencode(".jpg", frame)
            if not ok:
                continue

            result = inspect_image(encoded.tobytes())
            results.append(
                f"À {second:.1f} seconde(s) :\n{result}"
            )

        cap.release()

        if not results:
            raise RuntimeError("Aucune image exploitable.")

        answer = (
            "👑 RICHE BABE — Analyse vidéo\n\n"
            + "\n\n".join(results)
            + "\n\n⚠️ Les images sont échantillonnées. "
              "Cette analyse ne garantit pas le suivi continu "
              "de la boule pendant les mouvements."
        )

        bot.edit_message_text(
            answer[:4000],
            message.chat.id,
            status.message_id
        )

    except Exception as exc:
        print("Erreur analyse vidéo:", exc)
        bot.reply_to(
            message,
            "❌ Impossible d'analyser cette vidéo. "
            "Vérifie les dépendances, les clés API et le format."
        )

    finally:
        if path and os.path.exists(path):
            os.remove(path)


@bot.message_handler(func=lambda m: bool(m.text))
def other_messages(message):
    if not message.text.startswith("/"):
        bot.reply_to(
            message,
            "Envoie une photo ou une vidéo du jeu pour commencer."
        )


if __name__ == "__main__":
    print("Démarrage de Riche Babe...")
    bot.infinity_polling()
    
