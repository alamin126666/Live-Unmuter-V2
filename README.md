# 🚀 Live Auto-Unmute Bot — Ultra Premium Edition
> **Version 3.0 ✨** — Modern Design with Colored Buttons & Smooth UX

---

## ✨ নতুন ফিচারসমূহ (v3.0)

🎨 **প্রিমিয়াম UI/UX ডিজাইন**
- প্রতিটি বাটনে আলাদা কালার (Telegram's new feature)
- মডার্ন কার্ড-বেসড লেআউট
- প্রিমিয়াম ফন্ট স্টাইলিং
- গ্রেডিয়েন্ট এবং অ্যানিমেশন ইফেক্ট

⚡ **স্মুথ বোর্ড হ্যান্ডলিং**
- অপটিমাইজড পারফরম্যান্স
- দ্রুত রেসপন্স টাইম
- ইন্টেলিজেন্ট এরর হ্যান্ডলিং
- Flood Protection সহ

🎯 **উন্নত স্ট্যাটাস প্যানেল**
- রি���়েল-টাইম স্ট্যাটাস আপডেট
- ভিজ্যুয়াল প্রোগ্রেস ইন্ডিকেটর
- ডিটেইল পারফরম্যান্স মেট্রিক্স
- ইন্টারঅ্যাক্টিভ রিফ্রেশ

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

এই সংস্করণে `Dockerfile` ব্যবহার করা হয়েছে। এতে Railway/Nixpacks-এর
`externally-managed-environment` pip error এড়ানো হবে। GitHub repository-তে
প্রজেক্টের ভেতরের ফাইলগুলো (Dockerfile সহ) root directory-তে রাখুন।


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
   🚀 Starting Premium Live Auto-Unmute Bot...
   ✨ Version: 3.0 ✨ Ultra Premium
   ```
3. এই মেসেজ দেখলে ✅ সফলভাবে চালু হয়েছে!

---

## 📱 Bot ব্যবহার করুন — কুইক স্টার্ট

```
ধাপ ১ › /start পাঠান
        └ প্রিমিয়াম ওয়েলকাম স্ক্রিন দেখুন

ধাপ ২ › 🔐 লগিন করুন
        ├ ফোন নম্বর পাঠান
        ├ OTP কোড পাঠান
        └ ✅ লগিন সম্পন্ন

ধাপ ৩ › 🔗 চ্যানেল সেটআপ
        └ চ্যানেল লিঙ্ক পাঠান

ধাপ ৪ › 📡 লাইভ লিঙ্ক
        └ লাইভ লিঙ্ক পাঠান

ধাপ ৫ › 👑 অ্যাডমিন মোড চালু করুন
        └ আনমিউট ফিচার এনাবল করুন

ধাপ ৬ › 🚀 START BOT চাপুন
        └ বট স্বয়ংক্রিয় কাজ শুরু করবে
```

---

## 🎨 প্রিমিয়াম UI ফিচার

### কালার-কোডেড বাটন
- 🟢 **সবুজ** - স্টার্ট/সফল অ্যাকশন
- 🔴 **লাল** - স্টপ/বিপদজনক অ্যাকশন
- 🔵 **নীল** - সেটআপ/কনফিগারেশন
- 🟣 **বেগুনি** - অ্যাডমিন কন্ট্রোল
- 🟡 **হলুদ** - স্ট্যাটাস/তথ্য
- 🟠 **কমলা** - রিফ্রেশ/আপডেট

### মডার্ন লেআউট
```
╔═══════════════════════════════╗
║   🚀 Card Header Design       ║
╚═══════════════════════════════╝

▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
  Gradient Lines

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Premium Dividers

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 💎 Section Headers
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### স্মার্ট স্ট্যাটাস ইন্ডিকেটর
- 🟢🟢🟢🟢🟢 **FULLY OPERATIONAL** - সব সিস্টেম সচল
- 🟡🟡🟡⚪⚪ **SEARCHING** - লাইভ খোঁজা হচ্ছে
- 🔴🔴⚪⚪⚪ **OFFLINE** - বট বন্ধ আছে

---

## 🎯 প্রো টিপস

💡 **অ্যাডমিন মোড চালু রাখুন**
   └ মিউটেড মেম্বারদের অটোমেটিক আনমিউট করবে

💡 **স্ট্যাটাস প্যানেল চেক করুন**
   └ রিয়েল-টাইম পারফরম্যান্স দেখুন

💡 **রিফ্রেশ বাটন ব্যবহার করুন**
   └ লাইভ আপডেট পেতে

💡 **স্মুথ অপারেশন**
   └ বট নিজেই সব হ্যান্ডল করবে

---

## ⚙️ টেকনিক্যাল ফিচার

### স্মার্ট লাইভ ডিটেকশন
- অটোমেটিক লাইভ চেক (প্রতি 10 সেকেন্ডে)
- ইন্সট্যান্ট জয়েন সিস্টেম
- স্মুথ রিকানেক্ট

### ফ্লাড প্রটেকশন
- স্বয়ংক্রিয় Flood Wait হ্যান্ডলিং
- ইন্টেলিজেন্ট Retry Logic
- API Rate Limiting

### এরর হ্যান্ডলিং
- Graceful Error Recovery
- ডিটেইল এরর মেসেজ
- অটোমেটিক ফল-ব্যাক

### পারফরম্যান্স
- অপটিমাইজড মেমোরি ব্যবহার
- দ্রুত রেসপন্স টাইম
- স্মুথ অ্যানিমেশন

---

## ⚠️ গুরুত্বপূর্ণ নোট

- Railway **Free Plan** এ প্রতি মাসে $5 credit পাবেন (প্রায় 500 ঘণ্টা)
- Hobby Plan ($5/মাস) নিলে ২৪/৭ চলবে
- Session ফাইল `bot_session.session` Railway Volume-এ সেভ হবে
- Bot রিস্টার্ট হলে session থেকে auto-login হবে

---

## 🔧 সমস্যা সমাধান

| সমস্যা | সমাধান |
|--------|--------|
| Bot চালু হচ্ছে না | Variables ঠিকমতো দেওয়া হয়েছে কিনা চেক করুন |
| Login হচ্ছে না | API_ID ও API_HASH ঠিক আছে কিনা দেখুন |
| Flood Wait Error | অপেক্ষা করুন, বট স্বয়ংক্রিয় হ্যান্ডল করবে |
| Session Expired | Bot-এ /start দিয়ে আবার লগিন করুন |
| বাটন কালার দেখা যাচ্ছে না | Telegram app আপডেট করুন (latest version) |
| UI সঠিকভাবে দেখা যাচ্ছে না | /start কমান্ড আবার দিন |

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

---

## 🎨 ডিজাইন হাইলাইটস

### প্রিমিয়াম ফন্ট স্টাইলিং
- Bold headings for emphasis
- Monospace for codes/links
- Italic for descriptions
- Code blocks for technical info

### কার্ড-বেসড লেআউট
- সেকশন সেপারেশন
- ক্লিয়ার ভিজ্যুয়াল হায়ারার্কি
- ইনফরমেশন গ্রুপিং
- রিডেবিলিটি অপটিমাইজড

### অ্যানিমেশন ইফেক্ট
- স্মুথ ট্রানজিশন
- লোডিং ইন্ডিকেটর
- প্রোগ্রেস বার
- স্ট্যাটাস আপডেট

---

## 📊 ভার্সন হিস্ট্রি

**v3.0 (Current)** - Ultra Premium Edition
- ✨ সম্পূর্ণ নতুন প্রিমিয়াম UI/UX
- 🎨 কালার-কোডেড বাটন (Telegram নতুন ফিচার)
- ⚡ স্মুথ বোর্ড হ্যান্ডলিং
- 🎯 উন্নত স্ট্যাটাস প্যানেল
- 💎 প্রিমিয়াম ফন্ট এবং টাইপোগ্রাফি

**v2.0** - Premium Edition
- প্রিমিয়াম UI ডিজাইন
- উন্নত এরর হ্যান্ডলিং
- স্ট্যাটাস প্যানেল

**v1.0** - Initial Release
- বেসিক ফিচার
- অটো জয়েন/লিভ
- অটো আনমিউট

---

## 💎 প্রিমিয়াম অভিজ্ঞতা উপভোগ করুন!

**Made with ❤️ for Telegram Users**

```
╔═══════════════════════════════════╗
║  🚀 Live Auto-Unmute Bot v3.0    ║
║  ✨ Ultra Premium Edition         ║
╚═══════════════════════════════════╝
```
