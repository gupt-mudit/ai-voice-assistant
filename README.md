# 🏪 Shopkeeper Assistant - LiveKit Voice Agent

A voice AI assistant for small shopkeepers in India, powered by LiveKit Agents.

## 📁 Project Structure

```
shopkeeper-assistant/
├── agent.py                    # Main entry point for LiveKit agent
├── agents/
│   ├── __init__.py
│   └── shopkeeper_agent.py     # Agent definition with tools
├── tools/                      # → Symlink to ../tools (your existing tools)
│   ├── inventory_tool.py
│   └── reminder_tool.py
├── storage/                    # → Symlink to ../storage (your existing data)
│   ├── inventory_kb.txt
│   └── reminders_kb.txt
├── requirements.txt            # LiveKit dependencies
├── .env.template              # Environment variables template
└── README.md                  # This file
```

## ✨ Features

- **🎙️ Voice Conversations** in Hindi + English
- **📦 Inventory Management** - Track and update stock
- **⏰ Reminders** - Set and manage reminders
- **💵 Billing** - Create customer bills
- **⚡ Real-time** - Streaming audio with low latency
- **🔊 Natural** - Supports interruptions and natural turn-taking

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd shopkeeper-assistant

# Install LiveKit packages
pip install -r requirements.txt
```

### 2. Download Model Files

```bash
# Download VAD and turn detection models
python agent.py download-files
```

### 3. Setup Environment

**Option A: Local Testing (No signup required)**

```bash
# Start local LiveKit server in Docker
docker run -d -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev

# Copy environment template
cp .env.template .env.local

# Edit .env.local
nano .env.local
```

Set these values:
```bash
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
GOOGLE_API_KEY=your_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**Option B: LiveKit Cloud (Recommended)**

```bash
# 1. Sign up at https://cloud.livekit.io (free)
# 2. Create a project
# 3. Copy credentials

# Copy environment template
cp .env.template .env.local

# Edit and add your LiveKit Cloud credentials
nano .env.local
```

### 4. Run the Agent

**Console Mode** (voice in terminal - Python only):
```bash
python agent.py console
```

**Development Mode** (with playground):
```bash
python agent.py dev
```

Then open: https://cloud.livekit.io/playground

**Production Mode**:
```bash
python agent.py start
```

## 🎯 Usage Examples

### Testing in Console

```bash
python agent.py console
```

Try saying:
- **"Namaste"** → Agent greets you in Hindi
- **"5kg aloo add karo"** → Updates inventory
- **"Kitna stock hai?"** → Lists all inventory
- **"Kal subah 9 baje reminder set karo"** → Sets reminder
- **"Bill banao Ramesh ke liye"** → Creates customer bill

### Using the Playground

```bash
# Terminal 1: Start agent
python agent.py dev

# Open in browser:
# https://cloud.livekit.io/playground
# Click "Connect" and start speaking!
```

## 🛠️ Configuration

### Changing AI Providers

Edit `agent.py` to use different providers:

```python
session = AgentSession(
    # Speech-to-Text options:
    stt="assemblyai/universal-streaming:en",  # Current
    # stt="deepgram/nova-3:hi",               # For Hindi
    # stt="openai/whisper-1",                 # OpenAI Whisper
    
    # LLM options:
    llm="google/gemini-2.0-flash-exp",        # Current (Gemini)
    # llm="openai/gpt-4.1-mini",              # OpenAI
    # llm="anthropic/claude-3-5-sonnet",      # Claude
    
    # Text-to-Speech options:
    tts="elevenlabs/sarah:EXAVITQu4vr4xnSDxMaL",  # Current
    # tts="cartesia/sonic-2",                      # Cartesia
    # tts="openai/tts-1:alloy",                    # OpenAI
)
```

### Customizing the Agent

Edit `agents/shopkeeper_agent.py`:

**Change Instructions:**
```python
class ShopkeeperAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            Your custom instructions here...
            """
        )
```

**Add New Tools:**
```python
@function_tool
async def your_new_tool(
    self,
    context: RunContext,
    param: str
) -> str:
    """Tool description"""
    # Your logic here
    return result
```

## 🔧 Troubleshooting

### "Module not found: livekit"
```bash
pip install -r requirements.txt
```

### "Could not connect to LiveKit server"
```bash
# Check .env.local has correct LIVEKIT_URL
cat .env.local | grep LIVEKIT_URL

# For local: Make sure Docker container is running
docker ps
```

### "No audio in console mode"
```bash
# Check system audio settings
# Or use playground mode instead:
python agent.py dev
```

### "API key not found"
```bash
# Make sure .env.local exists and has all keys
ls -la .env.local
cat .env.local
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User (Browser/Phone)              │
└──────────────┬──────────────────────────────────────┘
               │ WebRTC Audio Stream
               ↓
┌──────────────────────────────────────────────────────┐
│              LiveKit Server                          │
│              (Cloud or Self-hosted)                  │
└──────────────┬──────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│         Shopkeeper Agent (agent.py)                  │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ STT → LLM → Function Tools → TTS           │   │
│  │  ↓      ↓         ↓            ↓           │   │
│  │  🎤    🧠    📦💵⏰        🔊          │   │
│  └─────────────────────────────────────────────┘   │
│                      ↓                               │
│           ┌──────────────────────┐                  │
│           │   Your Existing:     │                  │
│           │   - inventory_tool   │                  │
│           │   - reminder_tool    │                  │
│           │   - KB files         │                  │
│           └──────────────────────┘                  │
└──────────────────────────────────────────────────────┘
```

## 🚀 Deployment

### Deploy to LiveKit Cloud

```bash
# Make sure you're in shopkeeper-assistant folder
cd shopkeeper-assistant

# Install LiveKit CLI
brew install livekit-cli

# Authenticate
lk cloud auth

# Deploy
lk agent create
```

Your agent is now live globally! 🌍

## 📚 Documentation

- **LiveKit Agents**: https://docs.livekit.io/agents
- **Voice AI Guide**: https://docs.livekit.io/agents/build
- **API Reference**: https://docs.livekit.io/agents/models

## 🔗 Integrating with Frontend

### React/Next.js

```typescript
import { LiveKitRoom } from '@livekit/components-react';

function VoiceAssistant() {
  return (
    <LiveKitRoom
      serverUrl={LIVEKIT_URL}
      token={token}  // Get from your backend
      connect={true}
      audio={true}
    >
      <p>🎤 Speak to your assistant...</p>
    </LiveKitRoom>
  );
}
```

### Mobile Apps

- **React Native**: https://docs.livekit.io/home/quickstarts/react-native
- **Flutter**: https://docs.livekit.io/home/quickstarts/flutter
- **Swift**: https://docs.livekit.io/home/quickstarts/swift
- **Android**: https://docs.livekit.io/home/quickstarts/android

## 🆘 Support

- **Discord**: https://livekit.io/discord
- **GitHub**: https://github.com/livekit/agents
- **Docs**: https://docs.livekit.io

## 📝 License

Same as parent project
# ai-voice-assistant
