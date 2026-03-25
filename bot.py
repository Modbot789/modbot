import logging
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# --- ဒီနေရာမှာ သင့် Bot Token ကို အပြီးထည့်ပါ ---
TOKEN = "7773500418:AAFDWQmyY2bUDHMhM7-okO1H5xlFHaSObIo"

# ရိုင်းတဲ့ စကားလုံးများ စာရင်း
BAD_WORDS = ["လီး", "မအေလိုး", "သခိုး", "မအေလိုးမ", "ဖူးထုပ်"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Welcome Function ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id:
            continue

        user_name = new_user.first_name
        user_id = new_user.id
        group_name = update.message.chat.title
        
        # မြန်မာစံတော်ချိန် (UTC + 6:30)
        now = datetime.utcnow() + timedelta(hours=6, minutes=30)
        join_date = now.strftime("%d/%m/%Y")
        join_time = now.strftime("%I:%M %p")

        welcome_text = (
            f"🎊 *မင်္ဂလာပါ {user_name}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"📅 *Join Date:* {join_date}\n"
            f"⏰ *Join Time:* {join_time}\n"
            f"📍 *Group:* {group_name}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Group မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။"
        )
        await update.message.reply_text(text=welcome_text, parse_mode=ParseMode.MARKDOWN)

# --- Moderation Function (Auto Delete & Warn) ---
async def delete_and_warn(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        warn_msg = await context.bot.send_message(
            chat_id=chat_id, 
            text=f"⚠️ {user.first_name}၊ {reason} ကြောင့် စာကို ဖျက်လိုက်ပါတယ်။"
        )
        # ၅ စက္ကန့်ကြာရင် သတိပေးစာကို ပြန်ဖျက်မယ်
        await asyncio.sleep(5)
        await context.bot.delete_message(chat_id=chat_id, message_id=warn_msg.message_id)
    except Exception as e:
        logging.error(f"Error: {e}")

async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    text = update.message.text or ""
    
    # 1. Link & @ Check
    if re.search(r'http[s]?://|www\.|t\.me/', text) or "@" in text:
        await delete_and_warn(update, context, "Link/Username ပို့ခွင့်မရှိပါ")
        return

    # 2. Bad Words Check
    if any(word in text for word in BAD_WORDS):
        await delete_and_warn(update, context, "ရိုင်းစိုင်းသော စကားလုံး သုံးခွင့်မရှိပါ")
        return

    # 3. Emoji/Sticker/Animation Check
    if update.message.sticker or update.message.animation or (text and not re.search(r'[a-zA-Z0-9\u1000-\u109f]', text)):
        await delete_and_warn(update, context, "Emoji/Sticker သီးသန့် ပို့ခွင့်မရှိပါ")

def main():
    # Application building with hardcoded Token
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT | filters.Sticker | filters.ANIMATION, moderate_messages))

    print("Bot is running with hardcoded Token...")
    app.run_polling()

if __name__ == "__main__":
    main()
