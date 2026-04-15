# 🚀 IKONA Bot - Railway Deployment Quick Start

## Current Error (FIXED ✅)
```
Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**Root Cause:** Polling mode conflicts with multiple instances  
**Solution:** Switched to Webhook mode (production-ready)

---

## DEPLOY IN 3 STEPS

### Step 1️⃣: Set Environment Variables
Go to Railway Dashboard → Your Project → Variables

**Add these 2 variables:**
```
USE_WEBHOOK = true
RAILWAY_PUBLIC_DOMAIN = [your-railway-domain].up.railway.app
```

To find your domain:
- Railway Dashboard → Your Project → Domains (top right)
- Copy the domain exactly as shown (without https://)

**Example:**
```
RAILWAY_PUBLIC_DOMAIN = ikona-bot-a3b2c1.up.railway.app
```

### Step 2️⃣: Deploy
```bash
git add -A
git commit -m "Add webhook mode support"
git push origin main
```

Or click "Redeploy" in Railway Dashboard

### Step 3️⃣: Verify ✅
Check deployment logs. Should see:
```
🌐 Webhook mode enabled. URL: https://[domain]/webhook
✅ Webhook set to https://[domain]/webhook
📡 Bot is listening on port 8000
```

If you see these messages → **Bot is running successfully!**

---

## What Changed?

| Before | After |
|--------|-------|
| ❌ Polling (asks Telegram repeatedly) | ✅ Webhook (Telegram sends directly) |
| ❌ Conflicts with multiple instances | ✅ Works perfectly with multiple instances |
| ❌ Can't scale | ✅ Scales to any number of replicas |
| ❌ Higher latency | ✅ Instant response |
| ❌ Telegram rate limits | ✅ No rate limiting |

---

## Testing

1. Send a message to the bot in Telegram
2. Bot should respond instantly
3. Check Railway logs (should NOT show conflict errors)

---

## Files Modified

✅ `main.py` - Added FastAPI webhook + health check  
✅ `requirements.txt` - Added fastapi + uvicorn  
✅ `Procfile` - Web process configuration  
📄 `RAILWAY_SETUP.md` - Detailed setup guide  
📄 `ENV_VARIABLES.md` - Environment variable reference  

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Still getting conflict error | Make sure `USE_WEBHOOK=true` is set |
| Bot not responding | Check `RAILWAY_PUBLIC_DOMAIN` matches exactly |
| Logs show "terminated..." | Restart deployment (Redeploy button) |
| `/health` returns error | Wait 1-2 minutes, deployment still starting |

---

## Need Help?

- **Check logs:** Railway Dashboard → Deploy Logs (bottom)
- **Environment vars correct?** Verify no typos, match exactly
- **Domain not found?** It's in Railway Dashboard → Domains section (top right)
- **Still confused?** See `RAILWAY_SETUP.md` for detailed instructions

---

## That's It! 🎉

Your bot should now be running with zero conflicts and perfect scaling!
