import logging
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- သင့် Bot Token ကို အပြီးထည့်သွင်းထားပါသည် ---
TOKEN = "7773500418:AAFDWQmyY2bUDHMhM7-okO1H5xlFHaSObIo"

# ရိုင်းစိုင်းသော စကားလုံးများ စာရင်း
BAD_WORDS = ["လီး", "မအေလိုး", "သခိုး", "မအေလိုးမ", "ဖူးထုပ်"]

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Welcome Function (လူသစ်ဝင်လာလျှင် ကြိုဆိုရန်) ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
        
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

# --- Moderation Function (စာဖျက်ခြင်းနှင့် သတိပေးခြင်း) ---
async def delete_and_warn(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    try:
        # မူရင်းစာကို ဖျက်မည်
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        
        # သတိပေးစာ ပို့မည်
        warn_msg = await context.bot.send_message(
            chat_id=chat_id, 
            text=f"⚠️ {user.first_name}၊ {reason} ကြောင့် စာကို ဖျက်လိုက်ပါတယ်။"
        )
        
        # ၅ စက္ကန့်ကြာလျှင် သတိပေးစာကို ပြန်ဖျက်မည်
        await asyncio.sleep(5)
        await context.bot.delete_message(chat_id=chat_id, message_id=warn_msg.message_id)
    except Exception as e:
        logging.error(f"Error handling moderation: {e}")

# --- Message Filter Function (စစ်ဆေးခြင်း) ---
async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: 
        return
        
    text = update.message.text or update.message.caption or ""
    
    # ၁။ Link & @ Username စစ်ဆေးခြင်း
    if re.search(r'http[s]?://|www\.|t\.me/', text) or "@" in text:
        await delete_and_warn(update, context, "Link သို့မဟုတ် Username ပို့ခွင့်မရှိပါ")
        return

    # ၂။ ရိုင်းစိုင်းသော စကားလုံး စစ်ဆေးခြင်း
    if any(word in text for word in BAD_WORDS):
        await delete_and_warn(update, context, "ရိုင်းစိုင်းသော စကားလုံး သုံးခွင့်မရှိပါ")
        return

    # ၃။ Sticker နှင့် GIF/Animation စစ်ဆေးခြင်း
    if update.message.sticker or update.message.animation:
        await delete_and_warn(update, context, "Sticker သို့မဟုတ် GIF ပို့ခွင့်မရှိပါ")
        return

def main():
    # Application building
    app = Application.builder().token(TOKEN).build()

    # Welcome message handler
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    
    # Moderation handler (စာသား၊ စတစ်ကာ အကုန်စစ်မည်)
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND) & (~filters.StatusUpdate.ALL), moderate_messages))

    print("Bot is starting with the provided Token...")
    app.run_polling()

if __name__ == "__main__":
    main()
