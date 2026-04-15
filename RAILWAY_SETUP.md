# Railway Deployment Setup for IKONA Telegram Bot

## Fixed Issues
✅ **Webhook mode eliminates "multiple instances" conflict** - No more polling conflicts  
✅ **Supports credentials.json for Google Sheets**  
✅ **Moscow timezone support**  
✅ **Auto-recovery from failures**  

---

## Railway Configuration Steps

### 1. Environment Variables on Railway Dashboard

Add these variables in Railway dashboard:

```
USE_WEBHOOK=true
RAILWAY_PUBLIC_DOMAIN=your-railway-domain.up.railway.app
PORT=8000
```

**Note:** Replace `your-railway-domain` with your actual Railway domain (visible in Railway dashboard under "Domains")

### 2. Critical Variables (Already Configured)

These should already be set from previous deployment:
- `TELEGRAM_BOT_TOKEN` ✓
- `GOOGLE_SHEET_ID` ✓
- `OPENROUTER_API_KEY` ✓

### 3. Deploy Steps

1. **Push code to git** (make sure credentials.json is committed)
   ```bash
   git add -A
   git commit -m "Add webhook mode support"
   git push origin main
   ```

2. **Redeploy on Railway**
   - Go to Railway dashboard
   - Click "Redeploy"
   - Wait for build to complete (2-3 minutes)

3. **Verify webhook is set**
   - Check deployment logs for message:
   ```
   ✅ Webhook set to https://your-domain.up.railway.app/webhook
   ```

4. **Test the bot**
   - Send a message to bot
   - Check logs for processing confirmation

---

## Switching Between Modes

### Production (Webhook - Recommended)
```
USE_WEBHOOK=true
RAILWAY_PUBLIC_DOMAIN=your-domain.up.railway.app
```

### Development (Polling - Local Only)
```
USE_WEBHOOK=false
```
Or simply omit `USE_WEBHOOK` variable - defaults to polling

---

## Troubleshooting

### Issue: "Conflict: terminated by other getUpdates request"
**Cause:** Still using polling with multiple instances  
**Fix:** Ensure `USE_WEBHOOK=true` is set

### Issue: Webhook not receiving updates
**Check:**
1. `RAILWAY_PUBLIC_DOMAIN` matches your actual Railway domain
2. Domain is accessible: `https://your-domain.up.railway.app/health` should return 200
3. Check logs for "✅ Webhook set to..." message

### Issue: Google Sheets auth failure
**Check:**
1. `credentials.json` is in root directory of deployed app
2. Run these commands in Railway terminal:
   ```bash
   ls -la credentials.json
   python -c "import json; json.load(open('credentials.json'))" 
   ```

---

## How It Works

**Old Way (Polling)** ❌
- Bot repeatedly asks Telegram: "Any new messages?"
- Multiple instances = conflict (409 error)
- Can't scale horizontally

**New Way (Webhook)** ✅
- Telegram sends messages directly to bot
- No conflicts with multiple instances
- Scales perfectly, use multiple replicas if needed

---

## Health Checks

Railway will automatically ping `/health` endpoint to check if bot is alive:
- Status 200 = Bot is running
- Any error = Railway will restart

---

## Logs Monitoring

To see real-time logs:
```
Railway Dashboard → Deployments → Deploy Logs
```

Look for these success indicators:
```
🌐 Webhook mode enabled
✅ Webhook set to https://...
📡 Bot is listening on port 8000
```

---

## Important Notes

⚠️ **Do NOT use both polling and webhook at same time**  
⚠️ **RAILWAY_PUBLIC_DOMAIN must match your actual Railway domain**  
⚠️ **If changing domain, update environment variable immediately**  

---

## Quick Redeploy (after making changes)

```bash
git add -A
git commit -m "Bot updates"
git push origin main
# Then in Railway: click "Redeploy"
```
