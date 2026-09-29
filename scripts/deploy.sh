#!/bin/bash
# Deploy Income-Scout agent to Railway.app (24/7 autonomous)
set -e
echo "AI Deploying Income-Scout Agent"
pip install uagents web3	rainway init --name income-scout 2>/dev/null || true
railway up --detach
echo " Done. Monitor at https://railway.app"