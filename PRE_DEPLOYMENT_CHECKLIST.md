# ✅ IKONA Bot - Pre-Deployment Checklist

## Code Changes ✅ DONE
- [x] `main.py` - Webhook support added
- [x] `requirements.txt` - FastAPI + uvicorn added  
- [x] `Procfile` - Process definition added
- [x] `credentials.json` - Already in place

## Documentation ✅ DONE
- [x] `QUICK_START.md` - 3-step deployment guide
- [x] `RAILWAY_SETUP.md` - Full setup + troubleshooting
- [x] `ENV_VARIABLES.md` - Environment variable reference
- [x] `WEBHOOK_IMPLEMENTATION_SUMMARY.md` - Technical overview

---

## Railway Configuration Checklist

### Before Deployment
- [ ] Go to Railway Dashboard
- [ ] Select "telegram-bot" project
- [ ] Click "Variables" tab

### Environment Variables to Add
- [ ] Set `USE_WEBHOOK = true`
- [ ] Set `RAILWAY_PUBLIC_DOMAIN = [your-railway-domain].up.railway.app`
  - *Where to find: Railway dashboard → Domains (top right)*
- [ ] Verify these already exist:
  - [ ] `TELEGRAM_BOT_TOKEN`
  - [ ] `GOOGLE_SHEET_ID`
  - [ ] `OPENROUTER_API_KEY`

### Before Pushing Code
- [ ] Commit changes to git
  ```bash
  cd d:\PROJECTS\BOTS\ikona_ai\ —\ копия
  git add -A
  git commit -m "Add webhook mode support"
  git push origin main
  ```

### Deployment
- [ ] Code is pushed to GitHub
- [ ] Railway automatically detects push
- [ ] Railway rebuilds and deploys
- [ ] Wait 2-3 minutes for deployment

### After Deployment - Verify ✅

Check Railway Dashboard → Deploy Logs:

**Look for these messages (in this order):**
```
✅ 1. "🌐 Webhook mode enabled. URL: https://[domain]/webhook"
✅ 2. "✅ Webhook set to https://[domain]/webhook"
✅ 3. "📡 Bot is listening on port 8000"
```

**If you see all 3:** ✅ **SUCCESS! Bot is ready**

---

## Testing After Deployment

1. **Open Telegram**
   - Find your bot: @ikona_tattoo_bot_bot

2. **Send a message**
   - Any message to the bot

3. **Bot should respond**
   - If it responds → ✅ Working!
   - If no response after 10s → See Troubleshooting

4. **Check logs**
   - Go to Railway: Deploy Logs
   - Should see processing messages, NO error messages

---

## Troubleshooting

### Problem: Still seeing "Conflict: terminated..." error
**Solution:**
1. Check `USE_WEBHOOK=true` is set (not false)
2. Check `RAILWAY_PUBLIC_DOMAIN` is set correctly
3. Click "Redeploy" button in Railway
4. Wait 2 minutes, check logs again

### Problem: Bot not responding
**Check:**
1. Is `RAILWAY_PUBLIC_DOMAIN` exactly matching your domain?
2. Open in browser: `https://[your-domain].up.railway.app/health`
3. Should show: `{"status":"healthy"}`
4. If 404 error → deployment not ready, wait longer

### Problem: Deployment failed
**Check:**
1. See error in "Build Logs"? Note the error
2. Common: Python syntax error (check main.py)
3. Common: Missing dependency (check requirements.txt)

### Problem: Not sure if it's working
**Run this check:**
```bash
# Replace with your actual domain
curl https://your-domain.up.railway.app/health

# Should return:
# {"status":"healthy"}
```

---

## File Inventory

**Modified:**
- ✅ main.py (webhook implementation)
- ✅ requirements.txt (dependencies)

**Created:**
- ✅ Procfile (process config)
- ✅ QUICK_START.md (setup guide)
- ✅ RAILWAY_SETUP.md (detailed guide)
- ✅ ENV_VARIABLES.md (reference)
- ✅ WEBHOOK_IMPLEMENTATION_SUMMARY.md (tech overview)
- ✅ PRE_DEPLOYMENT_CHECKLIST.md (this file)

**Already Existed:**
- ✅ credentials.json (Google auth)
- ✅ All handler code (telegram commands)
- ✅ Google Sheets integration

---

## Critical Environment Variables

Copy these EXACTLY (replace domain with yours):

```
USE_WEBHOOK=true
RAILWAY_PUBLIC_DOMAIN=ikona-bot-a1b2c3d4.up.railway.app
```

**⚠️ IMPORTANT:** 
- No `https://` prefix in RAILWAY_PUBLIC_DOMAIN
- No `/webhook` suffix in RAILWAY_PUBLIC_DOMAIN
- Must match exactly what Railway shows in Domains

---

## Expected Timeline

| Step | Time |
|------|------|
| Set environment variables | 1 min |
| Push code to git | 1 min |
| Railway detects push | 10 sec |
| Build starts | 30 sec |
| Dependencies install | 60 sec |
| Bot starts | 30 sec |
| Webhook registered | 5 sec |
| **TOTAL** | **~3-4 minutes** |

After these 3-4 minutes, bot should be fully operational! ✅

---

## I'm Ready! ✅

If you:
- [x] Have Railway dashboard open
- [x] Found your domain
- [x] Read QUICK_START.md
- [x] Set 2 environment variables
- [x] Understand the deployment process

**→ You're ready to deploy!**

Deploy with:
```bash
git push origin main
```

Then monitor the logs in Railway and look for the 3 success messages. 
That's it! 🎉

---

## Questions?

- **"Where's my domain?"** → Railway Dashboard → Domains (top right)
- **"What if it fails?"** → Check BUILD LOGS tab, see the error
- **"How do I rollback?"** → Railway automatically keeps old deployments, can revert
- **"Is webhook secure?"** → Yes, uses HTTPS only
- **"Can I scale to multiple replicas?"** → YES! This is the whole point of webhooks!

---

## Success Indicators

After deployment, you should see:

✅ Bot responds instantly to messages  
✅ No "Conflict" errors in logs  
✅ Multiple messages processed simultaneously without errors  
✅ `/health` endpoint returns status: healthy  
✅ Webhook URL properly set with Telegram  

**If all above → You're done! 🎉**
