import telebot
from telebot import types
import json
import os
import datetime
import re

# ================= CONFIGURATION =================
BOT_TOKEN = '8925555849:AAGGxQ7-HsPCnITtbcRe_FNaKlTXl-vp2ac'
ADMIN_ID = 7876536711  # আপনার অ্যাডমিন আইডি / এডমিন প্রাইভেট আইডি

# চ্যানেল কনফিগারেশন
PAYMENT_CHANNEL_ID = "@newtaskprobot"   # পেমেন্ট প্রুফ চ্যানেল (ডিপোজিট, উইথড্র ও টাস্ক প্রুফ)
UPDATE_CHANNEL_ID = "@technical_nirob"     # বোটের আপডেট ও ঘোষণা দেওয়ার চ্যানেল
ADMIN_PRIVATE_LINK = "https://t.me/technical_nirob" # এডমিনের প্রাইভেট চ্যানেল/গ্রুপ লিঙ্ক

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE HELPER =================
FILES = {
    "users": "users.json",
    "settings": "settings.json",
    "tasks": "tasks.json",
    "shop": "shop.json",
    "deposit": "deposit.json",
    "withdraw": "withdraw.json",
    "logs": "logs.json"
}

# Initialize files
def init_db():
    default_settings = {
        "bot_name": "Gmail Earning Bot",
        "currency": "USDT",
        "trc20_address": "TYYourTRC20WalletAddressHereXYZ",
        "daily_bonus": 0.05,
        "bonus_cooldown": 24, # hours
        "min_deposit": 1.0,
        "min_withdraw": 2.0,
        "withdraw_fee": 0.1,
        "referral_reward": 0.1,
        "force_join_channels": ["@newtaskprobot", "@technical_nirob"], # ব্যবহারকারীর জন্য জয়েন করা বাধ্যতামূলক
        "force_join_active": True,
        "maintenance": False,
        "support_username": "@technical_nirob"
    }
    
    if not os.path.exists("settings.json"):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4)

    for key, filename in FILES.items():
        if key == "settings": continue
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

init_db()

def load_data(file_key):
    with open(FILES[file_key], "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file_key, data):
    with open(FILES[file_key], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Temporary memory state for admin/user wizard steps
USER_STATES = {}

# ================= TRANSLATIONS =================
TEXTS = {
    "en": {
        "welcome": "Welcome to Gmail Earning Bot! Choose your option below:",
        "must_join": "You must join our channels to use this bot:",
        "verify": "Verify Join",
        "main_menu": "Main Menu",
        "balance_msg": "👤 **User Profile**\n\n• Name: {name}\n• Username: @{username}\n• ID: `{id}`\n• Registered: {reg_date}\n\n💰 **Balance**: {balance} USDT\n💵 **Total Earned**: {total_earn} USDT\n📅 **Today Earned**: {today_earn} USDT\n\n📊 **Tasks Completed**: {completed_task}\n⏳ **Pending Tasks**: {pending_task}\n👥 **Referrals**: {ref_count} ({ref_income} USDT Earned)",
        "daily_bonus_claimed": "🎉 You claimed daily bonus of {amount} USDT!",
        "daily_bonus_wait": "⏳ Please wait {hours}h {minutes}m before claiming again.",
        "tasks_menu": "📋 Select Task Type:",
        "gmail_sell": "📧 Sell Gmail",
        "gmail_rent": "📧 Rent Gmail",
        "no_tasks": "No active tasks available right now.",
        "submit_gmail_prompt": "Please send the Gmail address for: **{task_name}**",
        "submit_pass_prompt": "Now send the Password for this Gmail:",
        "task_submitted": "✅ Task submitted successfully! Sent to Admin for review.",
        "refer_msg": "🎁 **Referral System**\n\nInvite friends and earn **{reward} USDT** per active user!\n\n🔗 Your Link: `https://t.me/{bot_username}?start={user_id}`\n\n• Total Referrals: {ref_count}\n• Total Earned: {ref_income} USDT",
        "deposit_msg": "📥 **Deposit USDT (TRC20)**\n\nSend USDT to the following TRC20 address:\n`{address}`\n\nMinimum Deposit: {min_dep} USDT\n\nAfter sending, click **Submit TXID**.",
        "withdraw_msg": "💳 **Withdraw USDT (TRC20)**\n\nMinimum Withdraw: {min_w} USDT\nWithdraw Fee: {fee} USDT\n\nYour Current Balance: {balance} USDT",
        "enter_withdraw_amount": "Enter the amount you want to withdraw:",
        "enter_withdraw_wallet": "Enter your USDT (TRC20) Wallet Address:",
        "withdraw_submitted": "✅ Withdrawal request submitted! Admin will review shortly.",
        "shop_msg": "🛒 **Gmail Shop**\n\nAvailable Stock: {stock} Gmails\nPrice per Gmail: {price} USDT",
        "not_enough_balance": "❌ Insufficient balance!",
        "lang_select": "Select your preferred language / ভাষা নির্বাচন করুন:",
        "maintenance": "🚧 Bot is under maintenance. Please try again later.",
        "banned": "❌ You are banned from using this bot."
    },
    "bn": {
        "welcome": "জিআইমেল আর্নিং বোটে আপনাকে স্বাগতম! নিচের অপশন নির্বাচন করুন:",
        "must_join": "বোট ব্যবহার করতে আমাদের সবকটি চ্যানেলে জয়েন করুন:",
        "verify": "ভেরিফাই করুন",
        "main_menu": "প্রধান মেনু",
        "balance_msg": "👤 **ইউজার প্রোফাইল**\n\n• নাম: {name}\n• ইউজারনেম: @{username}\n• আইডি: `{id}`\n• রেজিস্ট্রেশন: {reg_date}\n\n💰 **বর্তমান ব্যালেন্স**: {balance} USDT\n💵 **মোট আয়**: {total_earn} USDT\n📅 **আজকের আয়**: {today_earn} USDT\n\n📊 **সম্পন্ন টাস্ক**: {completed_task}\n⏳ **পেন্ডিং টাস্ক**: {pending_task}\n👥 **রেফারেল**: {ref_count} জন (আয়: {ref_income} USDT)",
        "daily_bonus_claimed": "🎉 আপনি {amount} USDT ডেইলি বোনাস পেয়েছেন!",
        "daily_bonus_wait": "⏳ আবার বোনাস নিতে {hours} ঘণ্টা {minutes} মিনিট অপেক্ষা করুন।",
        "tasks_menu": "📋 টাস্ক টাইপ নির্বাচন করুন:",
        "gmail_sell": "📧 জিমেইল সেল",
        "gmail_rent": "📧 জিমেইল রেন্ট",
        "no_tasks": "বর্তমানে কোনো সক্রিয় টাস্ক খালি নেই।",
        "submit_gmail_prompt": "**{task_name}** এর জন্য জিমেইল এড্রেসটি পাঠান:",
        "submit_pass_prompt": "এখন এই জিমেইলের পাসওয়ার্ডটি দিন:",
        "task_submitted": "✅ টাস্ক সফলভাবে জমা দেওয়া হয়েছে! এডমিন রিভিউ শেষে ব্যালেন্স যোগ হবে।",
        "refer_msg": "🎁 **রেফারেল সিস্টেম**\n\nবন্ধুদের ইনভাইট করুন এবং প্রতি রেফারে **{reward} USDT** আয় করুন!\n\n🔗 আপনার লিংক: `https://t.me/{bot_username}?start={user_id}`\n\n• মোট রেফারেল: {ref_count} জন\n• রেফার আয়: {ref_income} USDT",
        "deposit_msg": "📥 **ডিপোজিট USDT (TRC20)**\n\nনিচের TRC20 এড্রেসে USDT পাঠান:\n`{address}`\n\nসর্বনিম্ন ডিপোজিট: {min_dep} USDT\n\nটাকা পাঠানোর পর **Submit TXID** বাটনে ক্লিক করুন।",
        "withdraw_msg": "💳 **উইথড্র USDT (TRC20)**\n\nসর্বনিম্ন উইথড্র: {min_w} USDT\nউইথড্র ফি: {fee} USDT\n\nআপনার ব্যালেন্স: {balance} USDT",
        "enter_withdraw_amount": "উইথড্র করার পরিমাণ (Amount) লিখুন:",
        "enter_withdraw_wallet": "আপনার USDT (TRC20) ওয়ালেট এড্রেসটি দিন:",
        "withdraw_submitted": "✅ উইথড্র রিকোয়েস্ট জমা হয়েছে! শীঘ্রই এডমিন রিভিউ করবেন।",
        "shop_msg": "🛒 **জিমেইল শপ**\n\nস্টক আছে: {stock} টি\nপ্রতিটির দাম: {price} USDT",
        "not_enough_balance": "❌ আপনার পর্যাপ্ত ব্যালেন্স নেই!",
        "lang_select": "Select your preferred language / ভাষা নির্বাচন করুন:",
        "maintenance": "🚧 বোট মেইনটেন্যান্স এর কাজ চলছে। কিছু সময় পর চেষ্টা করুন।",
        "banned": "❌ আপনাকে বোটে ব্লক করা হয়েছে।"
    }
}

# ================= HELPER FUNCTIONS =================
def get_user(user_id):
    users = load_data("users")
    return users.get(str(user_id))

def create_user(user, referrer_id=None):
    users = load_data("users")
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "name": user.first_name,
            "username": user.username or "None",
            "lang": "en",
            "balance": 0.0,
            "total_earn": 0.0,
            "today_earn": 0.0,
            "last_earn_date": str(datetime.date.today()),
            "completed_task": 0,
            "pending_task": 0,
            "ref_count": 0,
            "ref_income": 0.0,
            "referred_by": referrer_id,
            "last_bonus": None,
            "is_banned": False,
            "reg_date": str(datetime.date.today())
        }
        save_data("users", users)
        
        # Reward Referrer
        if referrer_id and str(referrer_id) in users:
            settings = load_data("settings")
            ref_user = users[str(referrer_id)]
            ref_user["ref_count"] += 1
            ref_user["ref_income"] += settings["referral_reward"]
            ref_user["balance"] += settings["referral_reward"]
            ref_user["total_earn"] += settings["referral_reward"]
            save_data("users", users)
            try:
                bot.send_message(referrer_id, f"🎉 You received {settings['referral_reward']} USDT for referring a new user!")
            except: pass

def is_force_joined(user_id):
    settings = load_data("settings")
    if not settings.get("force_join_active"):
        return True
    
    for ch in settings.get("force_join_channels", []):
        try:
            ch_clean = ch if ch.startswith("@") or ch.startswith("-100") else f"@{ch}"
            member = bot.get_chat_member(ch_clean, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

def main_keyboard(user_id):
    u = get_user(user_id)
    lang = u["lang"] if u else "en"
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if lang == "bn":
        markup.add(
            types.KeyboardButton("💰 ব্যালেন্স"), types.KeyboardButton("🎁 ডেইলি বোনাস"),
            types.KeyboardButton("📋 টাস্ক"), types.KeyboardButton("🎁 রেফার"),
            types.KeyboardButton("💳 উইথড্র"), types.KeyboardButton("📥 ডিপোজিট"),
            types.KeyboardButton("🛒 শপ"), types.KeyboardButton("🏆 লিডারবোর্ড"),
            types.KeyboardButton("🌐 Language")
        )
    else:
        markup.add(
            types.KeyboardButton("💰 Balance"), types.KeyboardButton("🎁 Daily Bonus"),
            types.KeyboardButton("📋 Tasks"), types.KeyboardButton("🎁 Refer"),
            types.KeyboardButton("💳 Withdraw"), types.KeyboardButton("📥 Deposit"),
            types.KeyboardButton("🛒 Shop"), types.KeyboardButton("🏆 Leaderboard"),
            types.KeyboardButton("🌐 Language")
        )
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("🔑 Admin Panel"))
    return markup

def send_to_proof_channel(text):
    """পেমেন্ট এবং টাস্ক প্রুফ চ্যানেলে তথ্য পাঠাতে ব্যবহৃত হয়"""
    if PAYMENT_CHANNEL_ID:
        try:
            bot.send_message(PAYMENT_CHANNEL_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to proof channel: {e}")

def send_to_update_channel(text):
    """বোটের আপডেট অথবা এনাউন্সমেন্ট চ্যানেলে পাঠাতে ব্যবহৃত হয়"""
    if UPDATE_CHANNEL_ID:
        try:
            bot.send_message(UPDATE_CHANNEL_ID, text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to update channel: {e}")

# ================= COMMAND HANDLERS =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    settings = load_data("settings")

    if settings.get("maintenance") and user_id != ADMIN_ID:
        bot.send_message(user_id, TEXTS["en"]["maintenance"])
        return

    # Check referral
    args = message.text.split()
    referrer = args[1] if len(args) > 1 and args[1].isdigit() else None
    
    create_user(message.from_user, referrer)
    u = get_user(user_id)
    
    if u.get("is_banned"):
        bot.send_message(user_id, TEXTS[u['lang']]["banned"])
        return

    if not is_force_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in settings["force_join_channels"]:
            ch_name = ch if ch.startswith("@") else f"@{ch}"
            url_channel = ch_name.replace('@', '')
            markup.add(types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{url_channel}"))
        markup.add(types.InlineKeyboardButton(TEXTS[u['lang']]["verify"], callback_data="check_force_join"))
        bot.send_message(user_id, TEXTS[u['lang']]["must_join"], reply_markup=markup)
        return

    bot.send_message(user_id, TEXTS[u['lang']]["welcome"], reply_markup=main_keyboard(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "check_force_join")
def verify_force_join(call):
    if is_force_joined(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        u = get_user(call.from_user.id)
        bot.send_message(call.from_user.id, "✅ Verified!", reply_markup=main_keyboard(call.from_user.id))
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined all channels!", show_alert=True)

# ================= MAIN MENU HANDLERS =================
@bot.message_handler(func=lambda m: m.text in ["💰 Balance", "💰 ব্যালেন্স"])
def show_balance(message):
    u = get_user(message.from_user.id)
    lang = u["lang"]
    
    # Refresh today's earn if new day
    if u["last_earn_date"] != str(datetime.date.today()):
        u["today_earn"] = 0.0
        u["last_earn_date"] = str(datetime.date.today())
        users = load_data("users")
        users[str(message.from_user.id)] = u
        save_data("users", users)

    msg = TEXTS[lang]["balance_msg"].format(
        name=u["name"],
        username=u["username"],
        id=u["id"],
        reg_date=u["reg_date"],
        balance=round(u["balance"], 2),
        total_earn=round(u["total_earn"], 2),
        today_earn=round(u["today_earn"], 2),
        completed_task=u["completed_task"],
        pending_task=u["pending_task"],
        ref_count=u["ref_count"],
        ref_income=round(u["ref_income"], 2)
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Deposit", callback_data="deposit_btn"),
        types.InlineKeyboardButton("➖ Withdraw", callback_data="withdraw_btn")
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🎁 Daily Bonus", "🎁 ডেইলি বোনাস"])
def daily_bonus(message):
    uid = str(message.from_user.id)
    users = load_data("users")
    u = users[uid]
    lang = u["lang"]
    settings = load_data("settings")

    now = datetime.datetime.now()
    if u["last_bonus"]:
        last_b = datetime.datetime.fromisoformat(u["last_bonus"])
        cooldown = datetime.timedelta(hours=settings["bonus_cooldown"])
        if now < last_b + cooldown:
            rem = (last_b + cooldown) - now
            hours, remainder = divmod(rem.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            bot.send_message(message.chat.id, TEXTS[lang]["daily_bonus_wait"].format(hours=hours, minutes=minutes))
            return

    amount = settings["daily_bonus"]
    u["balance"] += amount
    u["total_earn"] += amount
    u["today_earn"] += amount
    u["last_bonus"] = now.isoformat()
    save_data("users", users)

    bot.send_message(message.chat.id, TEXTS[lang]["daily_bonus_claimed"].format(amount=amount))

@bot.message_handler(func=lambda m: m.text in ["🎁 Refer", "🎁 রেফার"])
def refer_menu(message):
    u = get_user(message.from_user.id)
    lang = u["lang"]
    settings = load_data("settings")
    bot_info = bot.get_me()

    msg = TEXTS[lang]["refer_msg"].format(
        reward=settings["referral_reward"],
        bot_username=bot_info.username,
        user_id=message.from_user.id,
        ref_count=u["ref_count"],
        ref_income=round(u["ref_income"], 2)
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🌐 Language"])
def lang_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en"),
        types.InlineKeyboardButton("বাংলা 🇧🇩", callback_data="set_lang_bn")
    )
    bot.send_message(message.chat.id, "Select Language / ভাষা নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def set_language(call):
    lang = call.data.split("_")[2]
    users = load_data("users")
    users[str(call.from_user.id)]["lang"] = lang
    save_data("users", users)
    bot.answer_callback_query(call.id, "Language Updated!")
    bot.send_message(call.from_user.id, "✅ Language changed successfully!", reply_markup=main_keyboard(call.from_user.id))

# ================= TASK SYSTEM =================
@bot.message_handler(func=lambda m: m.text in ["📋 Tasks", "📋 টাস্ক"])
def tasks_menu(message):
    u = get_user(message.from_user.id)
    lang = u["lang"]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(TEXTS[lang]["gmail_sell"], callback_data="task_list_sell"),
        types.InlineKeyboardButton(TEXTS[lang]["gmail_rent"], callback_data="task_list_rent")
    )
    bot.send_message(message.chat.id, TEXTS[lang]["tasks_menu"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_list_"))
def list_tasks(call):
    ttype = call.data.split("_")[2] # sell / rent
    tasks = load_data("tasks")
    u = get_user(call.from_user.id)
    lang = u["lang"]

    markup = types.InlineKeyboardMarkup()
    count = 0
    for tid, t in tasks.items():
        if t["type"] == ttype and t["status"] == "active":
            markup.add(types.InlineKeyboardButton(f"{t['title']} - {t['reward']} USDT", callback_data=f"start_task_{tid}"))
            count += 1

    if count == 0:
        bot.answer_callback_query(call.id, TEXTS[lang]["no_tasks"], show_alert=True)
    else:
        bot.send_message(call.from_user.id, "Select a task to complete:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("start_task_"))
def start_task_step1(call):
    tid = call.data.split("_")[2]
    tasks = load_data("tasks")
    task = tasks.get(tid)
    u = get_user(call.from_user.id)
    
    USER_STATES[call.from_user.id] = {"state": "AWAIT_GMAIL_EMAIL", "task_id": tid}
    bot.send_message(call.from_user.id, TEXTS[u["lang"]]["submit_gmail_prompt"].format(task_name=task["title"]), parse_mode="Markdown")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_GMAIL_EMAIL")
def process_task_email(message):
    email = message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        bot.send_message(message.chat.id, "❌ Invalid email format. Try again:")
        return

    USER_STATES[message.from_user.id]["email"] = email
    USER_STATES[message.from_user.id]["state"] = "AWAIT_GMAIL_PASS"
    u = get_user(message.from_user.id)
    bot.send_message(message.chat.id, TEXTS[u["lang"]]["submit_pass_prompt"])

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_GMAIL_PASS")
def process_task_pass(message):
    password = message.text.strip()
    state_data = USER_STATES.get(message.from_user.id)
    tid = state_data["task_id"]
    email = state_data["email"]

    logs = load_data("logs")
    sub_id = str(len(logs) + 1)
    logs[sub_id] = {
        "user_id": message.from_user.id,
        "task_id": tid,
        "email": email,
        "password": password,
        "status": "pending",
        "date": str(datetime.datetime.now())
    }
    save_data("logs", logs)

    users = load_data("users")
    users[str(message.from_user.id)]["pending_task"] += 1
    save_data("users", users)

    # এডমিন আইডিতে মেসেজ পাঠাবে
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Approve ✅", callback_data=f"app_task_{sub_id}"),
        types.InlineKeyboardButton("Reject ❌", callback_data=f"rej_task_{sub_id}")
    )
    bot.send_message(ADMIN_ID, f"📥 **New Task Submission (#{sub_id})**\n\nUser: `{message.from_user.id}`\nEmail: `{email}`\nPass: `{password}`", parse_mode="Markdown", reply_markup=markup)

    del USER_STATES[message.from_user.id]
    u = get_user(message.from_user.id)
    bot.send_message(message.chat.id, TEXTS[u["lang"]]["task_submitted"])

# ================= SHOP SYSTEM =================
@bot.message_handler(func=lambda m: m.text in ["🛒 Shop", "🛒 শপ"])
def shop_menu(message):
    shop = load_data("shop")
    u = get_user(message.from_user.id)
    lang = u["lang"]

    stock = len(shop.get("stock", []))
    price = shop.get("price", 0.5)

    msg = TEXTS[lang]["shop_msg"].format(stock=stock, price=price)
    
    markup = types.InlineKeyboardMarkup()
    if stock > 0:
        markup.add(types.InlineKeyboardButton("🛒 Buy 1 Gmail", callback_data="buy_gmail_1"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "buy_gmail_1")
def buy_gmail(call):
    uid = str(call.from_user.id)
    users = load_data("users")
    shop = load_data("shop")
    u = users[uid]
    
    price = shop.get("price", 0.5)
    stock = shop.get("stock", [])

    if u["balance"] < price:
        bot.answer_callback_query(call.id, TEXTS[u["lang"]]["not_enough_balance"], show_alert=True)
        return
    
    if not stock:
        bot.answer_callback_query(call.id, "Out of stock!", show_alert=True)
        return

    u["balance"] -= price
    acc = stock.pop(0)
    
    save_data("users", users)
    save_data("shop", shop)

    bot.send_message(call.from_user.id, f"✅ **Purchase Successful!**\n\nHere is your Gmail:\n`{acc['email']}:{acc['password']}`", parse_mode="Markdown")

# ================= DEPOSIT & WITHDRAW =================
@bot.message_handler(func=lambda m: m.text in ["📥 Deposit", "📥 ডিপোজিট"])
def deposit_menu(message):
    settings = load_data("settings")
    u = get_user(message.from_user.id)
    
    msg = TEXTS[u["lang"]]["deposit_msg"].format(address=settings["trc20_address"], min_dep=settings["min_deposit"])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Submit TXID 📥", callback_data="submit_txid"))
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "submit_txid")
def prompt_txid(call):
    USER_STATES[call.from_user.id] = {"state": "AWAIT_TXID"}
    bot.send_message(call.from_user.id, "Please enter your Deposit Transaction ID (TXID):")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_TXID")
def process_txid(message):
    txid = message.text.strip()
    USER_STATES[message.from_user.id]["txid"] = txid
    USER_STATES[message.from_user.id]["state"] = "AWAIT_DEP_AMOUNT"
    bot.send_message(message.chat.id, "Enter deposit amount (USDT):")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_DEP_AMOUNT")
def process_dep_amount(message):
    try:
        amount = float(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Invalid number. Enter amount again:")
        return

    txid = USER_STATES[message.from_user.id]["txid"]
    del USER_STATES[message.from_user.id]

    deps = load_data("deposit")
    dep_id = str(len(deps) + 1)
    deps[dep_id] = {"user_id": message.from_user.id, "txid": txid, "amount": amount, "status": "pending"}
    save_data("deposit", deps)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Approve ✅", callback_data=f"app_dep_{dep_id}"),
        types.InlineKeyboardButton("Reject ❌", callback_data=f"rej_dep_{dep_id}")
    )
    bot.send_message(ADMIN_ID, f"📥 **New Deposit (#{dep_id})**\nUser: `{message.from_user.id}`\nAmount: {amount} USDT\nTXID: `{txid}`", parse_mode="Markdown", reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Deposit request sent to admin!")

@bot.message_handler(func=lambda m: m.text in ["💳 Withdraw", "💳 উইথড্র"])
def withdraw_menu(message):
    settings = load_data("settings")
    u = get_user(message.from_user.id)
    
    msg = TEXTS[u["lang"]]["withdraw_msg"].format(min_w=settings["min_withdraw"], fee=settings["withdraw_fee"], balance=round(u["balance"], 2))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Request Withdraw 💸", callback_data="start_withdraw"))
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_withdraw")
def start_withdraw(call):
    u = get_user(call.from_user.id)
    settings = load_data("settings")
    if u["balance"] < settings["min_withdraw"]:
        bot.answer_callback_query(call.id, TEXTS[u["lang"]]["not_enough_balance"], show_alert=True)
        return
    USER_STATES[call.from_user.id] = {"state": "AWAIT_WITHDRAW_AMT"}
    bot.send_message(call.from_user.id, TEXTS[u["lang"]]["enter_withdraw_amount"])

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_WITHDRAW_AMT")
def process_w_amount(message):
    try:
        amt = float(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Enter valid number:")
        return

    u = get_user(message.from_user.id)
    settings = load_data("settings")

    if amt < settings["min_withdraw"] or amt > u["balance"]:
        bot.send_message(message.chat.id, "❌ Invalid or insufficient amount. Try again:")
        return

    USER_STATES[message.from_user.id]["amount"] = amt
    USER_STATES[message.from_user.id]["state"] = "AWAIT_WITHDRAW_WALLET"
    bot.send_message(message.chat.id, TEXTS[u["lang"]]["enter_withdraw_wallet"])

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id, {}).get("state") == "AWAIT_WITHDRAW_WALLET")
def process_w_wallet(message):
    wallet = message.text.strip()
    amt = USER_STATES[message.from_user.id]["amount"]
    del USER_STATES[message.from_user.id]

    users = load_data("users")
    users[str(message.from_user.id)]["balance"] -= amt
    save_data("users", users)

    w_data = load_data("withdraw")
    wid = str(len(w_data) + 1)
    w_data[wid] = {"user_id": message.from_user.id, "amount": amt, "wallet": wallet, "status": "pending"}
    save_data("withdraw", w_data)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Approve ✅", callback_data=f"app_w_{wid}"),
        types.InlineKeyboardButton("Reject ❌", callback_data=f"rej_w_{wid}")
    )
    bot.send_message(ADMIN_ID, f"💳 **New Withdraw (#{wid})**\nUser: `{message.from_user.id}`\nAmount: {amt} USDT\nWallet: `{wallet}`", parse_mode="Markdown", reply_markup=markup)
    u = get_user(message.from_user.id)
    bot.send_message(message.chat.id, TEXTS[u["lang"]]["withdraw_submitted"])

# ================= LEADERBOARD =================
@bot.message_handler(func=lambda m: m.text in ["🏆 Leaderboard", "🏆 লিডারবোর্ড"])
def leaderboard(message):
    users = load_data("users")
    sorted_users = sorted(users.values(), key=lambda x: x["total_earn"], reverse=True)[:10]

    msg = "🏆 **Top Earners Leaderboard**\n\n"
    for idx, u in enumerate(sorted_users, 1):
        uid_str = str(u['id'])
        masked_id = uid_str[:3] + "***" + uid_str[-3:]
        msg += f"{idx}. ID: `{masked_id}` - Total Earn: **{round(u['total_earn'], 2)} USDT**\n"

    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "🔑 Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    users = load_data("users")
    deps = load_data("deposit")
    withs = load_data("withdraw")

    pending_tasks = sum(1 for logs in load_data("logs").values() if logs["status"] == "pending")
    pending_deps = sum(1 for d in deps.values() if d["status"] == "pending")
    pending_withs = sum(1 for w in withs.values() if w["status"] == "pending")

    msg = f"🔑 **Admin Dashboard**\n\n👥 Total Users: {len(users)}\n⏳ Pending Tasks: {pending_tasks}\n📥 Pending Deposits: {pending_deps}\n💳 Pending Withdraws: {pending_withs}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Add Task", callback_data="admin_add_task"))
    markup.add(types.InlineKeyboardButton("🛒 Add Shop Stock", callback_data="admin_add_stock"))
    markup.add(types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton("📢 Join Admin Private Channel", url=ADMIN_PRIVATE_LINK)) # অ্যাডমিনের প্রাইভেট চ্যানেলে জয়েন লিংক
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

# ----------------- ADMIN FEATURE HANDLERS -----------------

# 1. Add Task Handler
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_task" and call.from_user.id == ADMIN_ID)
def admin_add_task_step1(call):
    USER_STATES[call.from_user.id] = {"state": "ADMIN_TASK_TITLE"}
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "✏️ **Enter Task Title:**\n(Example: Fresh Gmail 2024)", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and USER_STATES.get(m.from_user.id, {}).get("state") == "ADMIN_TASK_TITLE")
def admin_add_task_step2(message):
    USER_STATES[message.from_user.id]["title"] = message.text.strip()
    USER_STATES[message.from_user.id]["state"] = "ADMIN_TASK_TYPE"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Sell", callback_data="admin_ttype_sell"),
        types.InlineKeyboardButton("Rent", callback_data="admin_ttype_rent")
    )
    bot.send_message(message.chat.id, "⚙️ **Select Task Type:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_ttype_") and call.from_user.id == ADMIN_ID)
def admin_add_task_step3(call):
    ttype = call.data.split("_")[2] # sell / rent
    USER_STATES[call.from_user.id]["type"] = ttype
    USER_STATES[call.from_user.id]["state"] = "ADMIN_TASK_REWARD"
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "💵 **Enter Reward Amount per Task (in USDT):**\n(Example: 0.20)")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and USER_STATES.get(m.from_user.id, {}).get("state") == "ADMIN_TASK_REWARD")
def admin_add_task_step4(message):
    try:
        reward = float(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Invalid amount! Please enter a valid number (e.g. 0.15):")
        return

    state_data = USER_STATES[message.from_user.id]
    tasks = load_data("tasks")
    tid = str(len(tasks) + 1)
    
    tasks[tid] = {
        "title": state_data["title"],
        "type": state_data["type"],
        "reward": reward,
        "status": "active"
    }
    save_data("tasks", tasks)
    del USER_STATES[message.from_user.id]

    bot.send_message(message.chat.id, f"✅ **Task Added Successfully!**\n\n📌 Title: {state_data['title']}\n📁 Type: {state_data['type'].capitalize()}\n💰 Reward: {reward} USDT", parse_mode="Markdown")

# 2. Add Shop Stock Handler
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_stock" and call.from_user.id == ADMIN_ID)
def admin_add_stock_step1(call):
    USER_STATES[call.from_user.id] = {"state": "ADMIN_ADD_STOCK"}
    bot.answer_callback_query(call.id)
    msg = (
        "🛒 **Add Gmails to Shop Stock**\n\n"
        "Send accounts in `email:password` format.\n"
        "You can send multiple accounts line by line.\n\n"
        "**Example:**\n"
        "`user1@gmail.com:pass123`\n"
        "`user2@gmail.com:pass456`"
    )
    bot.send_message(call.from_user.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and USER_STATES.get(m.from_user.id, {}).get("state") == "ADMIN_ADD_STOCK")
def admin_add_stock_step2(message):
    lines = message.text.strip().split("\n")
    shop = load_data("shop")
    
    if "stock" not in shop:
        shop["stock"] = []
    if "price" not in shop:
        shop["price"] = 0.5

    added_count = 0
    for line in lines:
        if ":" in line:
            parts = line.strip().split(":", 1)
            email = parts[0].strip()
            password = parts[1].strip()
            shop["stock"].append({"email": email, "password": password})
            added_count += 1

    save_data("shop", shop)
    del USER_STATES[message.from_user.id]

    bot.send_message(message.chat.id, f"✅ **Successfully added {added_count} Gmail accounts to Shop Stock!**\n📦 Total Stock Available: {len(shop['stock'])}", parse_mode="Markdown")

# 3. Broadcast Handler
@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast" and call.from_user.id == ADMIN_ID)
def admin_broadcast_step1(call):
    USER_STATES[call.from_user.id] = {"state": "ADMIN_BROADCAST"}
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "📢 **Enter the message you want to broadcast to all users:**\n\n(Supports Text, Photos with caption, etc.)", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and USER_STATES.get(m.from_user.id, {}).get("state") == "ADMIN_BROADCAST")
def admin_broadcast_step2(message):
    users = load_data("users")
    success = 0
    failed = 0

    bot.send_message(message.chat.id, f"🚀 Broadcasting to {len(users)} users...")

    for uid in users.keys():
        try:
            bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
        except Exception:
            failed += 1

    del USER_STATES[message.from_user.id]
    bot.send_message(message.chat.id, f"✅ **Broadcast Completed!**\n\n🎯 Success: {success}\n❌ Failed/Blocked: {failed}")

# Admin Handlers for Approving Actions
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_task_"))
def approve_task(call):
    if call.from_user.id != ADMIN_ID: return
    sub_id = call.data.split("_")[2]
    logs = load_data("logs")
    sub = logs.get(sub_id)

    if sub and sub["status"] == "pending":
        sub["status"] = "approved"
        save_data("logs", logs)

        tasks = load_data("tasks")
        reward = tasks[sub["task_id"]]["reward"]

        users = load_data("users")
        u = users[str(sub["user_id"])]
        u["balance"] += reward
        u["total_earn"] += reward
        u["today_earn"] += reward
        u["completed_task"] += 1
        u["pending_task"] = max(0, u["pending_task"] - 1)
        save_data("users", users)

        bot.send_message(sub["user_id"], f"✅ Your task (#{sub_id}) was approved! Received {reward} USDT.")
        bot.edit_message_text(f"✅ Approved Task #{sub_id}", call.message.chat.id, call.message.message_id)
        
        # পেমেন্ট প্রুফ চ্যানেলে তথ্য শেয়ার করা
        send_to_proof_channel(f"🎉 **New Task Approved!**\n\n👤 User ID: `{sub['user_id']}`\n💰 Earned: **{reward} USDT**\n✅ Status: Approved")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_task_"))
def reject_task(call):
    if call.from_user.id != ADMIN_ID: return
    sub_id = call.data.split("_")[2]
    logs = load_data("logs")
    sub = logs.get(sub_id)

    if sub and sub["status"] == "pending":
        sub["status"] = "rejected"
        save_data("logs", logs)

        users = load_data("users")
        u = users[str(sub["user_id"])]
        u["pending_task"] = max(0, u["pending_task"] - 1)
        save_data("users", users)

        bot.send_message(sub["user_id"], f"❌ Your task (#{sub_id}) was rejected.")
        bot.edit_message_text(f"❌ Rejected Task #{sub_id}", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_dep_"))
def approve_deposit(call):
    if call.from_user.id != ADMIN_ID: return
    dep_id = call.data.split("_")[2]
    deps = load_data("deposit")
    dep = deps.get(dep_id)

    if dep and dep["status"] == "pending":
        dep["status"] = "approved"
        save_data("deposit", deps)

        users = load_data("users")
        u = users[str(dep["user_id"])]
        u["balance"] += dep["amount"]
        save_data("users", users)

        bot.send_message(dep["user_id"], f"✅ Your deposit of {dep['amount']} USDT was approved!")
        bot.edit_message_text(f"✅ Approved Deposit #{dep_id}", call.message.chat.id, call.message.message_id)
        
        # পেমেন্ট প্রুফ চ্যানেলে তথ্য শেয়ার করা
        send_to_proof_channel(f"📥 **Successful Deposit!**\n\n👤 User ID: `{dep['user_id']}`\n💰 Amount: **{dep['amount']} USDT**\n✅ Status: Completed")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_dep_"))
def reject_deposit(call):
    if call.from_user.id != ADMIN_ID: return
    dep_id = call.data.split("_")[2]
    deps = load_data("deposit")
    dep = deps.get(dep_id)

    if dep and dep["status"] == "pending":
        dep["status"] = "rejected"
        save_data("deposit", deps)

        bot.send_message(dep["user_id"], f"❌ Your deposit request (#{dep_id}) was rejected.")
        bot.edit_message_text(f"❌ Rejected Deposit #{dep_id}", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_w_"))
def approve_withdraw(call):
    if call.from_user.id != ADMIN_ID: return
    wid = call.data.split("_")[2]
    w_data = load_data("withdraw")
    w = w_data.get(wid)

    if w and w["status"] == "pending":
        w["status"] = "approved"
        save_data("withdraw", w_data)

        bot.send_message(w["user_id"], f"✅ Your withdrawal of {w['amount']} USDT has been processed!")
        bot.edit_message_text(f"✅ Approved Withdraw #{wid}", call.message.chat.id, call.message.message_id)
        
        # পেমেন্ট প্রুফ চ্যানেলে বার্তা পাঠাবে
        send_to_proof_channel(f"💳 **Successful Withdrawal!**\n\n👤 User ID: `{w['user_id']}`\n💸 Amount: **{w['amount']} USDT**\n✅ Status: Paid")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rej_w_"))
def reject_withdraw(call):
    if call.from_user.id != ADMIN_ID: return
    wid = call.data.split("_")[2]
    w_data = load_data("withdraw")
    w = w_data.get(wid)

    if w and w["status"] == "pending":
        w["status"] = "rejected"
        save_data("withdraw", w_data)

        # Refund Balance
        users = load_data("users")
        users[str(w["user_id"])]["balance"] += w["amount"]
        save_data("users", users)

        bot.send_message(w["user_id"], f"❌ Your withdrawal request (#{wid}) was rejected and funds were refunded.")
        bot.edit_message_text(f"❌ Rejected Withdraw #{wid}", call.message.chat.id, call.message.message_id)

# ================= START BOT =================
print("Bot is running...")
bot.infinity_polling()