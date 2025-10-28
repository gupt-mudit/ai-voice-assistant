# 🚀 Deploy Shopkeeper Assistant to LiveKit Cloud

## Prerequisites
✅ You already have:
- LiveKit Cloud account (shopkeeper-assistant-moxxznit.livekit.cloud)
- API credentials in `.env.local`
- Working voice assistant

## Deployment Steps

### 1️⃣ **Install LiveKit CLI**

```bash
# Install LiveKit CLI globally
pip install livekit-cli

# Or using pipx (recommended)
pipx install livekit-cli
```

### 2️⃣ **Test Locally First**

```bash
# Make sure your agent works locally
python agent.py dev

# This connects to LiveKit Cloud and gives you a test URL
# Visit the URL in your browser to test
```

### 3️⃣ **Deploy to LiveKit Cloud**

Option A: **Deploy from your machine (Simple)**

```bash
# Deploy directly from your local code
livekit-cli deploy agent.py

# Follow the prompts:
# - Enter your LiveKit URL: wss://shopkeeper-assistant-moxxznit.livekit.cloud
# - Enter API Key: APIedRvPxzq8UDn
# - Enter API Secret: P8lzuISTYM0hvr7wEBepcVIZ2x40V9wWHVxl57cWjGX
```

Option B: **Deploy from Git (Production)**

```bash
# 1. Push your code to GitHub/GitLab
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# 2. Deploy from Git
livekit-cli deploy \
  --git-url <your-repo-url> \
  --entrypoint agent.py
```

### 4️⃣ **Set Environment Variables**

After deployment, set your API keys:

```bash
# Set environment variables on LiveKit Cloud
livekit-cli env set GOOGLE_API_KEY "AIzaSyCMhtfavaKmvhGXgFhM6sock1ioafAChTQ"
livekit-cli env set DEEPGRAM_API_KEY "971fd854250e6a602e0a33822bc4d852c5366cf5"
livekit-cli env set CARTESIA_API_KEY "<your-cartesia-key>"
```

### 5️⃣ **Get Your Agent URL**

After deployment, you'll get:
```
✅ Agent deployed successfully!
📍 Agent URL: https://agents.livekit.io/<your-agent-id>
```

### 6️⃣ **Connect to Your Agent**

**Option A: Web Interface**
- Visit the agent URL
- Click "Join Room"
- Start talking!

**Option B: Mobile/Desktop App**
- Use LiveKit's sample apps
- Enter your room URL
- Connect with video/audio

**Option C: Phone Integration**
- Set up Twilio SIP trunk
- Connect to your LiveKit room
- Shopkeepers call a phone number!

---

## 🔧 Configuration

### Auto-scaling
LiveKit Cloud automatically scales your agent:
- Starts new instances when busy
- Shuts down when idle
- Pay only for active time

### Monitoring
View logs and metrics:
```bash
# View logs
livekit-cli logs

# View running agents
livekit-cli agent list
```

### Update Deployment
```bash
# Update code
git push origin main

# Redeploy
livekit-cli deploy --update
```

---

## 📞 **Next Steps: Phone Integration**

To let shopkeepers **call a phone number** and talk to your AI:

1. **Get Twilio Account**
   - Sign up at twilio.com
   - Get a phone number (~$1/month)

2. **Configure SIP Trunk**
   ```bash
   # Connect Twilio to LiveKit
   livekit-cli sip create-trunk \
     --name "Shopkeeper Calls" \
     --provider twilio
   ```

3. **Done!**
   - Shopkeepers dial the number
   - Your AI answers
   - Real-time voice conversation

---

## 💰 **Cost Estimate**

LiveKit Cloud pricing:
- **Free Tier**: 10,000 minutes/month
- **After free tier**: ~$0.005/minute (~₹0.40/minute)

For 100 shopkeepers using 30 min/month each:
- 3,000 minutes/month
- **Cost: FREE** (within free tier!)

---

## 🐛 **Troubleshooting**

**Agent not starting?**
```bash
# Check logs
livekit-cli logs --follow

# Check agent status
livekit-cli agent list
```

**Environment variables not working?**
```bash
# List all env vars
livekit-cli env list

# Update env var
livekit-cli env set KEY "value"
```

**Need to rollback?**
```bash
# Rollback to previous version
livekit-cli deploy --rollback
```

---

## 🎯 **Production Checklist**

Before going live:
- [ ] Tested in `dev` mode
- [ ] All API keys added as env vars
- [ ] Tested with real Hindi/English queries
- [ ] Monitored logs for errors
- [ ] Set up error alerts
- [ ] Created backup of storage/
- [ ] Documented for team
- [ ] Load tested with multiple users

---

Need help? Check:
- LiveKit Docs: https://docs.livekit.io/agents/
- LiveKit Discord: https://livekit.io/discord
