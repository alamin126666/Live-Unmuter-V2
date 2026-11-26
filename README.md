# 🤖 Live Auto-Unmute Bot — Railway Deploy Guide
> Premium Edition v2.0 ✨

---

## 📋 প্রয়োজনীয় তথ্য সংগ্রহ

### ১. BOT_TOKEN নিন
1. Telegram-এ [@BotFather](https://t.me/BotFather) খুলুন
2. `/newbot` পাঠান
3. নাম ও username দিন
4. Token কপি করুন → `BOT_TOKEN`

### ২. API_ID ও API_HASH নিন
1. [https://my.telegram.org](https://my.telegram.org) যান
2. ফোন নম্বর দিয়ে লগিন করুন
3. **"API development tools"** ক্লিক করুন
4. App তৈরি করুন (যেকোনো নাম দিন)
5. `api_id` → `API_ID` এবং `api_hash` → `API_HASH`

### ৩. ADMIN_ID নিন
1. Telegram-এ [@userinfobot](https://t.me/userinfobot) খুলুন
2. `/start` পাঠান
3. **Id:** এর নম্বরটি → `ADMIN_ID`

---

## 🚀 Railway-তে Deploy করুন

### ধাপ ১ — Account তৈরি
👉 [railway.app](https://railway.app) এ GitHub দিয়ে Sign Up করুন

### ধাপ ২ — New Project তৈরি
1. Dashboard থেকে **"New Project"** ক্লিক করুন
2. **"Deploy from GitHub repo"** বেছে নিন
   - অথবা **"Empty Project"** → তারপর ZIP আপলোড

### ধাপ ৩ — ফাইল আপলোড (GitHub ছাড়া)
1. **"Empty Project"** → **"Add Service"** → **"GitHub Repo"**
2. অথবা Railway CLI ব্যবহার করুন:
   ```bash
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```

### ধাপ ৪ — Environment Variables সেট করুন
1. Service এর **"Variables"** ট্যাবে যান
2. **"Add Variable"** ক্লিক করুন, একে একে দিন:

   | Variable   | মান                        |
   |------------|---------------------------|
   | BOT_TOKEN  | আপনার bot token           |
   | API_ID     | আপনার api id (শুধু সংখ্যা)|
   | API_HASH   | আপনার api hash            |
   | ADMIN_ID   | আপনার telegram user id    |

### ধাপ ৫ — Deploy চালু করুন
1. Variables সেট করার পর **"Deploy"** বাটন চাপুন
2. **"Logs"** ট্যাবে দেখুন:
   ```
   🤖 Live Auto-Unmute Bot 2.0 ✨ Premium শুরু হচ্ছে...
   ```
3. এই মেসেজ দেখলে ✅ সফলভাবে চালু হয়েছে!

---

## 📱 Bot ব্যবহার করুন

```
ধাপ ১ › /start পাঠান
ধাপ ২ › 🔐 লগিন করুন বাটন চাপুন
ধাপ ৩ › ফোন নম্বর ও কোড দিন
ধাপ ৪ › 🔗 চ্যানেল সেট করুন
ধাপ ৫ › 📡 লাইভ লিঙ্ক সেট করুন
ধাপ ৬ › 🟢 START BOT চাপুন
```

---

## ⚠️ গুরুত্বপূর্ণ নোট

- Railway **Free Plan** এ প্রতি মাসে $5 credit পাবেন (প্রায় 500 ঘণ্টা)
- Hobby Plan ($5/মাস) নিলে ২৪/৭ চলবে
- Session ফাইল `bot_user_session.session` Railway Volume-এ সেভ হবে
- Bot রিস্টার্ট হলে আবার লগিন করতে হতে পারে

---

## 🔧 সমস্যা সমাধান

| সমস্যা | সমাধান |
|--------|--------|
| Bot চালু হচ্ছে না | Variables ঠিকমতো দেওয়া হয়েছে কিনা চেক করুন |
| Login হচ্ছে না | API_ID ও API_HASH ঠিক আছে কিনা দেখুন |
| Flood Wait Error | কিছুক্ষণ অপেক্ষা করুন, স্বয়ংক্রিয় ঠিক হবে |
| Session Expired | Bot-এ /start দিয়ে আবার লগিন করুন |

---

## 📞 সংক্ষিপ্ত Railway CLI Deploy

```bash
# ১. CLI ইনস্টল
npm install -g @railway/cli

# ২. লগিন
railway login

# ৩. প্রজেক্ট তৈরি
railway init

# ৪. Deploy
railway up

# ৫. Variables সেট
railway variables set BOT_TOKEN=xxx API_ID=xxx API_HASH=xxx ADMIN_ID=xxx

# ৬. লগ দেখুন
railway logs
```
