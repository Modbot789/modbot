import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "7773500418:AAEhHlmx8dQCWpYQJY97i0Gc2ZT6qe7Izss"

# စည်းကမ်းချက်များ
GROUP_RULES = """
📜 **GROUP_ စည်းကမ်းချက်များ**
၁။ တစ်ဦးကိုတစ်ဦး ရိုင်းစိုင်းစွာ မပြောဆိုရ။
၂။ Spam Link များ၊ ကြော်ငြာများ မတင်ရ။
၃။ ဘာသာရေး၊ နိုင်ငံရေးနှင့် ပတ်သက်ပြီး အငြင်းပွားမှုများ မပြုလုပ်ရ။
"""

# အရင်ပို့ထားတဲ့ Message ID ကို မှတ်ထားဖို့ variable
last_welcome_id = {}

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    for new_user in update.message.new_chat_members:
        # Bot ကိုယ်တိုင်ဝင်လာတာဆိုရင် ဘာမှမလုပ်ပါနဲ့
        if new_user.id == context.bot.id:
            continue

        # အရင်ပို့ထားတဲ့ Welcome Message ရှိရင် ဖျက်ပါ
        if chat_id in last_welcome_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_welcome_id[chat_id])
            except:
                pass

        user_name = new_user.first_name
        welcome_text = f"မင်္ဂလာပါ **{user_name}** ခင်ဗျာ! \nGroup ကနေ နွေးထွေးစွာ ကြိုဆိုပါတယ်။"
        
        # Rules အတွက် Button ထည့်ခြင်း
        keyboard = [[InlineKeyboardButton("📜 စည်းကမ်းချက်များဖတ်ရန်", callback_data='show_rules')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Message ID ကို သိမ်းထားမယ်
        last_welcome_id[chat_id] = sent_message.message_id

        # ၅ မိနစ်နေရင် ဖျက်ဖို့ Timer ပေးမယ်
        context.job_queue.run_once(delete_msg, 300, data=sent_message.message_id, chat_id=chat_id)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'show_rules':
        # ခလုတ်နှိပ်ရင် စည်းကမ်းချက်ကို Alert အနေနဲ့ပြမယ် (သို့မဟုတ်) စာသားပြောင်းမယ်
        await query.answer(text=GROUP_RULES, show_alert=True)

async def delete_msg(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except:
        pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(CallbackQueryHandler(button_click)) # Button နှိပ်တာကို စစ်ဆေးဖို့

    print("Bot Version 2 is running...")
    app.run_polling()
