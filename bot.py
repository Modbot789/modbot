import logging
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- Bot Token ---
TOKEN = "7773500418:AAFDWQmyY2bUDHMhM7-okO1H5xlFHaSObIo"

# ရိုင်းစိုင်းသော စကားလုံးများ
BAD_WORDS = ["လီး", "မအေလိုး", "သခိုး", "မအေလိုးမ", "ဖူးထုပ်"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Admin Check Function ---
async def is_admin(update: Update):
    user_id = update.effective_user.id
    chat_member = await update.effective_chat.get_member(user_id)
    return chat_member.status in ['administrator', 'creator']

# --- Welcome Function ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id: continue
        now = datetime.utcnow() + timedelta(hours=6, minutes=30)
        welcome_text = (
            f"🎊 *မင်္ဂလာပါ {new_user.first_name}*\n"
            f"🆔 *User ID:* `{new_user.id}`\n"
            f"📅 *Date:* {now.strftime('%d/%m/%Y')}\n"
            f"📍 *Group:* {update.message.chat.title}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Group မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။"
        )
        await update.message.reply_text(text=welcome_text, parse_mode=ParseMode.MARKDOWN)

# --- Admin Commands ---

# 1. Ban User (/ban)
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /ban လို့ ရိုက်ပါ။")
        return
    
    target_user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=target_user.id)
    await update.message.reply_text(f"🚫 {target_user.first_name} ကို Group ထဲက အပြီးထုတ်လိုက်ပါပြီ။")

# 2. Mute User (/mute)
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /mute လို့ ရိုက်ပါ။")
        return

    target_user = update.message.reply_to_message.from_user
    # 24 နာရီ စကားပြောပိတ်ထားမည်
    until_date = datetime.utcnow() + timedelta(hours=24)
    from telegram import ChatPermissions
    permissions = ChatPermissions(can_send_messages=False)
    
    await context.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=target_user.id, permissions=permissions, until_date=until_date)
    await update.message.reply_text(f"🔇 {target_user.first_name} ကို ၂၄ နာရီ စကားပြောပိတ်လိုက်ပါပြီ။")

# 3. Unmute User (/unmute)
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /unmute လို့ ရိုက်ပါ။")
        return

    target_user = update.message.reply_to_message.from_user
    from telegram import ChatPermissions
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True)
    
    await context.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=target_user.id, permissions=permissions)
    await update.message.reply_text(f"🔊 {target_user.first_name} အခု စကားပြန်ပြောလို့ ရပါပြီ။")

# --- Moderation Function ---
async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update): return
    text = update.message.text or update.message.caption or ""
    
    # Check for Links, Bad Words, and Stickers
    if re.search(r'http[s]?://|www\.|t\.me/', text) or "@" in text or \
       any(word in text for word in BAD_WORDS) or \
       update.message.sticker or update.message.animation:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        except: pass

def main():
    app = Application.builder().token(TOKEN).build()

    # Welcome & Moderation
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    
    # Admin Commands
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))

    # All messages moderation
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND) & (~filters.StatusUpdate.ALL), moderate_messages))

    print("Bot with Admin Commands is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
