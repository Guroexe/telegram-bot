# IKONA Bot Environment Variables - Railway Config

## Webhook Mode (Production) - RECOMMENDED

```ini
# Enable webhook instead of polling
USE_WEBHOOK=true

# Your Railway domain (found in Railway dashboard under "Domains")
RAILWAY_PUBLIC_DOMAIN=ikona-bot-xyz.up.railway.app

# Port (leave as default unless changed)
PORT=8000
```

## Polling Mode (Development/Local) - NOT for Railway with multiplicas

```ini
# Completely omit this or set to false:
# USE_WEBHOOK=false
```

## Required Variables (Should Already Be Set)

```ini
TELEGRAM_BOT_TOKEN=8080984118:AAEjdBYzSrp-W88qdT-jvl7M-Sb7mi1JAxI
GOOGLE_SHEET_ID=1NWTT8LYzMJljRnSvdx92_wKDdYi91zvnc_T1WumStmQ
OPENROUTER_API_KEY=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
```

## How to Find RAILWAY_PUBLIC_DOMAIN

1. Open Railway dashboard
2. Go to your "telegram-bot" project
3. Click the project name
4. Look for "Domains" section (right side)
5. Copy the domain (e.g., `ikona-bot-123xyz.up.railway.app`)
6. Add to environment variable

## Issues?

### "Conflict: terminated by other getUpdates"
→ Set `USE_WEBHOOK=true` and `RAILWAY_PUBLIC_DOMAIN`

### Bot not responding
→ Verify `RAILWAY_PUBLIC_DOMAIN` matches exactly (no typos)
→ Check `/health` endpoint returns 200

### Webhook never received
→ Make sure domain is public/accessible
→ Restart deployment after changing domain
