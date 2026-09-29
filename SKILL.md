---
name: income-scout-agent
description: "Scans AI networks for income, executes work autonomously."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Income-Scout Agent

Autonomous agent that scans AI networks and gig platforms for income opportunities, registers where possible, completes qualifying tasks, and delivers a daily earnings report.

## Platforms

| Platform | Scan | Register | Work | Pay |
|---|---|---|---|---|
| Crowdgen (Appen) | Yes | Partial (email verify) | Yes | Bank/PayPal |
| Fetch.ai Agentverse | Yes | Yes (wallet) | Yes | FET tokens |
| SingularityNET | Yes | Yes (wallet) | Yes | AGIX tokens |
| Gitcoin bounties | Yes | Yes (wallet) | Partial | Crypto |
| Lionbridge | Yes | Partial | Yes | Bank/PayPal |

## Prerequisites

1. Crypto wallet (small ETH for gas)
2. Telegram bot from @BotFather
3. Email aliases (SimpleLogin/AnonAddy)

## Setup

Install deps:
```
uv pip install uagents web3
```

Configure Telegram:
```
hermes bot setup telegram
```

Add wallet to ~/.hermes/.env:
```
FET_PRIVATE_KEY=your_key_here
ETH_PRIVATE_KEY=your_key_here
TELEGRAM_ALERT_CHAT_ID=your_id
```

Register Fetch.ai agent (one-time):
```
uv run --with uagents --no-project python -c "from uagents import Agent; a=Agent(name='scout',seed='your_seed_phrase'); print(a.wallet.address()); a.run()"
```

## Cron Jobs

Crowdgen scan (every 4h):
```
hermes cron add crowdgen-scan \
  --schedule "0 */4 * * *" \
  --prompt "Scan https://app.crowdgen.com/ for AI annotation projects. Extract title, pay, requirements. Report to Telegram. If pay >$15/hr and <3 reqs, auto-apply." \
  --deliver telegram --deliver-chat-id "${TELEGRAM_ALERT_CHAT_ID}"
```

Fetch.ai marketplace (every 2h):
```
hermes cron add fetchai-scan \
  --schedule "0 */2 * * *" \
  --prompt "Check https://agentverse.ai/marketplace for agents requesting data labeling, scraping, moderation. Report FET estimates." \
  --deliver telegram --deliver-chat-id "${TELEGRAM_ALERT_CHAT_ID}"
```

Gitcoin bounties (daily):
```
hermes cron add gitcoin-bounties \
  --schedule "0 9 * * *" \
  --prompt "Check https://gitcoin.co/bounties/ for AI/data bounties >0.1 ETH. Extract title, amount, skills, deadline." \
  --deliver telegram --deliver-chat-id "${TELEGRAM_ALERT_CHAT_ID}"
```

## Payment Webhook

```
hermes webhook subscribe wallet-payment \
  --events "payment_received" \
  --prompt "New payment: {payload.amount} {payload.token}. Activate scan for next opportunity." \
  --deliver telegram
```

## Deploy 24/7

Railway.app:
```
railway init --name income-scout && railway up --detach
```

Windows service (NSSM):
```
nssm install income-scout "hermes" "cron run"
```

Render.com:
```
echo 'services:
 - type: worker
   name: income-scout
   env: python
   buildCommand: "pip install uagents"
   startCommand: "hermes cron run"' > render.yaml
```

## Daily Report Format (Telegram @ 20:00 UTC)

```
Income-Seeking Agent - Sep 30
Opportunities: 12
  Crowdgen: 3 proyectos ($18/hr)
  Fetch.ai: 4 agent requests
  Gitcoin: 3 bounties (~0.85 ETH)
Earnings: 0.03 ETH + 0.23 FET
Tasks done: 2 completed, 1 pending review
```

## Limitations

- KYC platforms: escanea y reporta, pero registro requiere verificacion humana.
- Wallet: tu creas, agente registra y trabaja despues.
- Pago via bank: configuracion manual inicial.
- Calidad creativa: puede requerir revision humana.

## Related Skills

- skill: hermes-agent
- skill: telegram-userbot
- skill: antigravity-cli
