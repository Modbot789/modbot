import logging
import re
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# --- Bot Token (ဒီနေရာမှာ သင့် Token ကို သေချာထည့်ပါ) ---
TOKEN = "7773500418:AAFDWQmyY2bUDHMhM7-okO1H5xlFHaSObIo"

# ပိတ်ပင်ထားသော စကားလုံးများ
BAD_WORDS = ["လီး", "မအေလိုး", "သခိုး", "မအေလိုးမ", "ဖူးထုပ်", "စောက်ဖုတ်"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Admin ဟုတ်မဟုတ် စစ်ဆေးသည့် Function
async def is_admin(update: Update):
    if update.effective_chat.type == "private":
        return False
    user_id = update.effective_user.id
    chat_member = await update.effective_chat.get_member(user_id)
    return chat_member.status in ['administrator', 'creator']

# --- လူသစ်ကြိုဆိုခြင်း (Welcome) ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_user in update.message.new_chat_members:
        if new_user.id == context.bot.id:
            continue
            
        # မြန်မာစံတော်ချိန် တွက်ချက်ခြင်း (UTC + 6:30)
        now = datetime.utcnow() + timedelta(hours=6, minutes=30)
        date_str = now.strftime('%d/%m/%Y')
        
        welcome_msg = (
            f"👋 *မင်္ဂလာပါ {new_user.first_name}*\n\n"
            f"🆔 *User ID:* `{new_user.id}`\n"
            f"📅 *Date:* {date_str}\n"
            f"📍 *Group:* {update.message.chat.title}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"ကျွန်တော်တို့ Group မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။ "
            f"စည်းကမ်းများကို လိုက်နာပေးဖို့ မေတ္တာရပ်ခံအပ်ပါတယ်ခင်ဗျာ။"
        )
        await update.message.reply_text(text=welcome_msg, parse_mode=ParseMode.MARKDOWN)

# --- Admin Commands ---

# 1. Ban (/ban)
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /ban လို့ ရိုက်ပါ။")
        return
    
    target = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await update.message.reply_text(f"🚫 {target.first_name} ကို Group ထဲက ထုတ်ပစ်လိုက်ပါပြီ။")

# 2. Mute (/mute)
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /mute လို့ ရိုက်ပါ။")
        return
    
    target = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)
    # ၂၄ နာရီ ပိတ်ထားမည်
    until = datetime.utcnow() + timedelta(hours=24)
    
    await context.bot.restrict_chat_member(update.effective_chat.id, target.id, permissions, until_date=until)
    await update.message.reply_text(f"🔇 {target.first_name} ကို ၂၄ နာရီ စကားပြောပိတ်လိုက်ပါပြီ။")

# 3. Unmute (/unmute)
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User ကို Reply ပြန်ပြီး /unmute လို့ ရိုက်ပါ။")
        return
    
    target = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    
    await context.bot.restrict_chat_member(update.effective_chat.id, target.id, permissions)
    await update.message.reply_text(f"🔊 {target.first_name} စကားပြန်ပြောလို့ ရပါပြီ။")

# --- စာသားများကို စစ်ဆေးခြင်း (Moderation) ---
async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or await is_admin(update):
        return
    
    msg_text = update.message.text or update.message.caption or ""
    
    # Link များ၊ ဆဲစာများ သို့မဟုတ် Sticker/GIF များကို စစ်ဆေးခြင်း
    if (re.search(r'http[s]?://|www\.|t\.me/', msg_text) or 
        any(word in msg_text for word in BAD_WORDS) or 
        update.message.sticker or update.message.animation):
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
        except:
            pass

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    
    # Filter မလုပ်စေချင်သော message များမှအပ အကုန်စစ်မည်
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), monitor_messages))

    print("Welcome Bot is online...")
    app.run_polling()

if __name__ == "__main__":
    main()
