import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ------------------------------------------
# SETTINGS
# ------------------------------------------
BOT_TOKEN = "8589567214:AAELGLGvN6PwlU7yPuOeI3QHIfFNC2S3xOY"
ADMIN_ID = 6718205476        # Apna Telegram numeric ID
JOIN_CHANNEL = "@ashad_paise"  # Join verify channel

REF_BONUS = 5               # Per refer ₹
BONUS_AMOUNT = 2            # Daily bonus ₹
WITHDRAW_MIN = 20           # Minimum withdraw

bot = telebot.TeleBot(BOT_TOKEN)

# Database (simple in-memory)
users = {}
upi_links = {}

# ------------------------------------------
# START COMMAND
# ------------------------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.chat.id

    if uid not in users:
        users[uid] = {"balance": 0, "bonus_claim": 0}

        # Refer system
        if len(msg.text.split()) > 1:
            ref = msg.text.split()[1]
            try:
                ref = int(ref)
                if ref != uid:
                    users[ref]["balance"] += REF_BONUS
                    bot.send_message(ref, f"🎉 New refer! +₹{REF_BONUS}")
            except:
                pass

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Verify Join", callback_data="verify"))
    bot.send_message(uid,
                     "👋 *Welcome!* 🔥\n\n"
                     "👉 Earn per refer\n"
                     "👉 Daily bonus\n"
                     "👉 Withdraw UPI\n\n"
                     "First join channel👇",
                     parse_mode="Markdown",
                     reply_markup=kb)

# ------------------------------------------
# VERIFY JOIN
# ------------------------------------------
@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    uid = c.message.chat.id
    member = bot.get_chat_member(JOIN_CHANNEL, uid)

    if member.status in ["member", "administrator", "creator"]:
        menu(uid)
    else:
        bot.answer_callback_query(c.id, "⚠ Join channel first!", show_alert=True)

# ------------------------------------------
# MAIN MENU
# ------------------------------------------
def menu(uid):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("👤 Balance", callback_data="bal"),
        InlineKeyboardButton("🎁 Bonus", callback_data="bonus")
    )
    kb.add(
        InlineKeyboardButton("👥 Refer", callback_data="refer"),
        InlineKeyboardButton("💸 Withdraw", callback_data="wd")
    )
    kb.add(InlineKeyboardButton("🔗 Add UPI", callback_data="upi"))

    bot.send_message(uid, "📲 *Main Menu*", parse_mode="Markdown", reply_markup=kb)

# ------------------------------------------
# MENU HANDLERS
# ------------------------------------------
@bot.callback_query_handler(func=lambda c: c.data == "bal")
def bal(c):
    uid = c.message.chat.id
    bot.answer_callback_query(c.id)
    bot.send_message(uid, f"💰 Balance: ₹{users[uid]['balance']}")

@bot.callback_query_handler(func=lambda c: c.data == "bonus")
def bonus(c):
    uid = c.message.chat.id
    bot.answer_callback_query(c.id)

    if users[uid]["bonus_claim"] == 1:
        bot.send_message(uid, "⏳ Bonus only 1 time in 20 hours.")
        return

    users[uid]["balance"] += BONUS_AMOUNT
    users[uid]["bonus_claim"] = 1

    bot.send_message(uid, f"🎉 Bonus added! +₹{BONUS_AMOUNT}")

@bot.callback_query_handler(func=lambda c: c.data == "refer")
def refer(c):
    uid = c.message.chat.id
    bot.answer_callback_query(c.id)

    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.send_message(uid, f"👥 *Your Refer Link:*\n{link}", parse_mode="Markdown")

# ------------------------------------------
# UPI SAVE
# ------------------------------------------
@bot.callback_query_handler(func=lambda c: c.data == "upi")
def upi(c):
    uid = c.message.chat.id
    bot.answer_callback_query(c.id)
    bot.send_message(uid, "🔗 Send your UPI ID:")
    bot.register_next_step_handler(c.message, save_upi)

def save_upi(msg):
    uid = msg.chat.id
    upi_links[uid] = msg.text
    bot.send_message(uid, "✅ UPI saved!")

# ------------------------------------------
# WITHDRAW
# ------------------------------------------
@bot.callback_query_handler(func=lambda c: c.data == "wd")
def wd(c):
    uid = c.message.chat.id
    bot.answer_callback_query(c.id)

    if uid not in upi_links:
        bot.send_message(uid, "⚠ Pehle UPI add karo.")
        return

    if users[uid]["balance"] < WITHDRAW_MIN:
        bot.send_message(uid, f"❌ Minimum withdraw ₹{WITHDRAW_MIN}")
        return

    amount = users[uid]["balance"]
    upi = upi_links[uid]

    users[uid]["balance"] = 0

    # Send request to admin
    bot.send_message(ADMIN_ID,
                     f"💸 *Withdraw Request*\n\n"
                     f"User: {uid}\n"
                     f"Amount: ₹{amount}\n"
                     f"UPI: {upi}",
                     parse_mode="Markdown")

    bot.send_message(uid, "📨 Request sent! Payment 24 hours me mil jayega.")

# ------------------------------------------
# RUN BOT
# ------------------------------------------
bot.polling(none_stop=True)
