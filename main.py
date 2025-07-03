from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"users": {}, "channels": {}, "fixed_links": [], "config": {"min_members": 150, "max_channels_per_user": 2, "post_times": ["03:00", "06:00", "09:00", "12:00"]}, "last_posted_message_ids": {}, "banned_users": []}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

data = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bem-vindo ao Divulgador VIP! Use /enviar para cadastrar seu canal.")

async def enviar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in data["banned_users"]:
        await update.message.reply_text("⛔ Você está banido de enviar canais.")
        return

    args = context.args
    if len(args) != 1:
        await update.message.reply_text("🔧 Use o comando assim: /enviar @nomedoseucanal")
        return

    canal = args[0]
    if canal in data["channels"]:
        await update.message.reply_text("❌ Esse canal já está na lista para aprovação.")
        return

    if user_id not in data["users"]:
        data["users"][user_id] = {"username": update.effective_user.username, "channels": []}

    if len(data["users"][user_id]["channels"]) >= data["config"]["max_channels_per_user"]:
        await update.message.reply_text("⚠️ Você já atingiu o limite de canais permitidos.")
        return

    data["channels"][canal] = {"status": "pending", "owner": user_id}
    data["users"][user_id]["channels"].append(canal)
    save_data(data)

    await update.message.reply_text(f"⏳ Seu canal {canal} foi enviado para aprovação. Aguarde!")

async def aprovar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(os.getenv('ADMIN_ID', '0')):
        return

    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Use: /aprovar @canal")
        return

    canal = args[0]
    if canal not in data["channels"]:
        await update.message.reply_text("Canal não encontrado.")
        return

    data["channels"][canal]["status"] = "approved"
    save_data(data)
    await update.message.reply_text(f"✅ Canal {canal} aprovado com sucesso!")

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("aprovar", aprovar))
    print("Bot iniciado com sucesso.")
    app.run_polling()
