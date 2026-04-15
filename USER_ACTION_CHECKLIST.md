# 📋 IKONA Bot - User Action Checklist

## Current Issue ❌
```
telegram.error.Conflict: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

## Root Cause ❌
Bot is still in **polling mode** because environment variables are NOT set on Railway

## Solution ✅
Set 2 environment variables → Webhook mode activates → Errors gone

---

## ACTION CHECKLIST - DO THIS RIGHT NOW

### ☐ STEP 1: Get Your Railway Domain (1 min)
- [ ] Open https://railway.app
- [ ] Click on "telegram-bot" project
- [ ] Click "Domains" button (top right)
- [ ] Copy the domain (example: `ikona-bot-a1b2c3.up.railway.app`)
- [ ] **WRITE IT DOWN:**
  ```
  My domain: ________________________
  ```

### ☐ STEP 2: Set Environment Variables (1 min)
- [ ] In Railway Dashboard, click "Variables" tab
- [ ] Click "New Variable"
- [ ] **First variable:**
  - Name: `USE_WEBHOOK`
  - Value: `true`
  - Click "Add"
- [ ] **Second variable:**
  - Name: `RAILWAY_PUBLIC_DOMAIN`
  - Value: `[your-domain-from-step-1]`
  - Click "Add"

### ☐ STEP 3: Redeploy (2-3 min)
- [ ] Click "Redeploy" button (top right)
- [ ] Wait for deployment to complete
- [ ] You'll see a green checkmark when done

### ☐ STEP 4: Verify Success (1 min)
- [ ] Click "Deploy Logs" tab
- [ ] Scroll to the bottom
- [ ] Look for these messages:
  ```
  🌐 Webhook mode enabled
  ✅ Webhook set to https://...
  📡 Bot is listening on port 8000
  ```
- [ ] If you see all 3 messages → ✅ SUCCESS!

### ☐ STEP 5: Test the Bot (1 min)
- [ ] Open Telegram
- [ ] Send a message to your bot
- [ ] Bot should respond **instantly** (<1 second)
- [ ] Send another message
- [ ] Should work **without errors** ✅

---

## Expected Timeline

| Step | Duration | Status |
|------|----------|--------|
| Step 1: Get domain | 1 min | |
| Step 2: Set variables | 1 min | |
| Step 3: Redeploy | 2-3 min | |
| Step 4: Verify logs | 1 min | |
| Step 5: Test bot | 1 min | |
| **TOTAL** | **~6-8 min** | ⏱️ |

**After ~8 minutes, bot will be working perfectly!**

---

## What You're Fixing

### Before (Polling - BROKEN ❌)
```
Bot keeps asking Telegram: "Any updates?"
Multiple instances = Conflict!
Error every few seconds: 409 Conflict
```

### After (Webhook - FIXED ✅)
```
Telegram sends updates directly to bot
No conflicts!
Instant responses
Works perfectly
```

---

## IMPORTANT REMINDERS

⚠️ **Must set BOTH variables:**
- `USE_WEBHOOK=true`
- `RAILWAY_PUBLIC_DOMAIN=your-domain`

⚠️ **Copy domain EXACTLY:**
- ✅ `ikona-bot-a1b2c3.up.railway.app`
- ❌ `ikona-bot-a1b2c3.up.railway.app` (different domain)
- ❌ `https://ikona-bot-a1b2c3.up.railway.app` (has https://)
- ❌ `ikona-bot-a1b2c3.up.railway.app/webhook` (has /webhook)

⚠️ **Spelling matters:**
- ✅ `USE_WEBHOOK` (uppercase, underscore)
- ✅ `RAILWAY_PUBLIC_DOMAIN` (uppercase, underscores)
- ✅ `true` (lowercase)

---

## Help If Stuck

### I can't find the domain
→ Railway Dashboard → Your project → Top right → "Domains" button → Copy the domain

### I set variables but still seeing errors
→ Did you click "Redeploy"? That's the final step!
→ Wait 3 minutes, check logs again

### I don't see the success messages
→ Scroll to the bottom of Deploy Logs
→ Look for timestamps with "2026-04-16 0x:xx:xx"
→ Search for "✅ Webhook set"

### Bot still not responding
→ Send a test message
→ Check if you see the message in console
→ If no error in logs, bot is working!

---

## Quick Reference

**Your domain (write here):**
```
_________________________________
```

**Variables to set:**
```
USE_WEBHOOK=true
RAILWAY_PUBLIC_DOMAIN=[YOUR-DOMAIN]
```

**Success message to look for:**
```
✅ Webhook set to https://[YOUR-DOMAIN]/webhook
```

---

## Final Checklist Before You Start

- [ ] I have Railway dashboard open
- [ ] I can see "telegram-bot" project
- [ ] I found the domain in "Domains" button
- [ ] I copied the domain (with .up.railway.app)
- [ ] I'm ready to set variables

**If all checkboxes checked → YOU'RE READY!**

---

## DO THIS NOW

1. Open Railway.app
2. Go to Variables
3. Add:
   - `USE_WEBHOOK=true`
   - `RAILWAY_PUBLIC_DOMAIN=your-domain`
4. Click Redeploy
5. Wait 3 minutes
6. **✅ Done!**

---

## After It's Fixed

✅ Bot responds instantly  
✅ No more errors  
✅ Can scale to multiple instances  
✅ Production-ready  

**That's it! You'll have a perfectly working bot!** 🎉

---

**Time to fix: ~10 minutes**  
**Difficulty: Easy**  
**Result: Professional production-grade bot**  

🚀 **LET'S GO!**
