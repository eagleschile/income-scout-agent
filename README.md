# Income-Scout Agent

Autonomous AI agent that scans AI networks and gig platforms for income opportunities, registers where possible, completes qualifying tasks, and reports earnings via Telegram.

Deployed on **Render** → auto-scans every 2-4 hours → alerts via Telegram.

## Platforms

| Platform | Scan | Register | Work | Pay |
|---|---|---|---|---|
| Crowdgen (ex-Appen) | ✅ | Partial (email) | ✅ | Bank/PayPal |
| Fetch.ai Agentverse | ✅ | ✅ Wallet | ✅ | FET tokens |
| SingularityNET | ✅ | ✅ Wallet | ✅ | AGIX tokens |
| Gitcoin bounties | ✅ | ✅ Wallet | Partial | Crypto |
| Lionbridge | ✅ | Partial | ✅ | Bank/PayPal |

## Quick Deploy (Render + GitHub)

1. **Fork this repo** to your GitHub account (`eagleschile/income-scout-agent`)
2. **Create a Render.com account** → click "New Web Service" → "Connect GitHub" → select this repo
3. **Add secrets** in Render dashboard:
   - `TELEGRAM_BOT_TOKEN` (from @BotFather)
   - `TELEGRAM_ALERT_CHAT_ID` (from @userinfobot)
   - `FET_PRIVATE_KEY` (Fetch.ai wallet key)
   - `ETH_PRIVATE_KEY` (Ethereum wallet key)
4. **Click "Create Web Service"** → agent deploys in 2 minutes and starts scanning

## Local Development

```bash
pip install -r requirements.txt
python main.py
```

## What the Agent Does

- **Crowdgen scan (every 4h):** Finds new AI data annotation projects, reports pay rates
- **Fetch.ai marketplace (every 2h):** Queries Agentverse for agents requesting services
- **Gitcoin bounties (daily):** Finds AI/web3 bounties >0.1 ETH
- **Lionbridge (every 4h):** Checks for new AI training opportunities
- **Daily report (20:00 UTC):** Summary of opportunities found and earnings

## Requirements

- Crypto wallet (small ETH for gas ~$10)
- Telegram bot (free, via @BotFather)
- No KYC needed for crypto networks

## Limitations

- Traditional platforms (Crowdgen, Lionbridge) require human registration + KYC
- Crypto networks: wallet setup is manual, but agent self-registers after
- Creative work quality may need human review before submission

## License

MIT
