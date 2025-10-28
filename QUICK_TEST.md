# 🧪 Quick Test Guide - Shopkeeper Assistant

## 🚀 Start the Agent

```bash
cd shopkeeper-assistant
python agent.py console
```

## 🎮 Console Controls

- **`Ctrl+B`** - Toggle between Text Mode / Audio Mode
- **`Q`** - Quit

## 📝 Test in TEXT Mode (Works Now!)

The console starts in TEXT mode by default. Just type and press Enter.

### Try These Commands:

```
You: Namaste
AI: (Should greet you in Hindi)

You: 5kg aloo add karo
AI: (Should update inventory)

You: kitna stock hai?
AI: (Should list inventory)

You: onion ka price 12 rupees hai
AI: (Should update price)

You: kal subah 9 baje reminder set karo
AI: (Should set reminder)
```

## 🎤 Test in AUDIO Mode (Requires API Keys)

Press `Ctrl+B` to switch to audio mode.

**NOTE:** You need these API keys for audio:
- ✅ GOOGLE_API_KEY (have it!)
- ✅ ELEVENLABS_API_KEY (have it!)
- ❌ ASSEMBLYAI_API_KEY (need to get - free at https://www.assemblyai.com/)

To add AssemblyAI key:
```bash
# Sign up at https://www.assemblyai.com/ (free)
# Get your API key
# Add to .env.local:
echo "ASSEMBLYAI_API_KEY=your_key_here" >> .env.local
```

## 🔍 What to Expect

### Text Mode Output:
```
==================================================
     Livekit Agents - Console
==================================================
Press [Ctrl+B] to toggle between Text/Audio mode, [Q] to quit.

Text Mode
─────────
You: 5kg aloo add karo
Agent: ✅ Added 5kg potatoes to inventory
```

### Audio Mode Output:
```
Audio Mode (Press Ctrl+B to switch back)
─────────────────────────────────────────
[Listening...]
You: "5kg aloo add karo"
Agent: "Theek hai, maine 5 kilo aloo stock mein add kar diya"
[🔊 Playing audio...]
```

## ✅ What Works Right Now

- ✅ Text mode (no extra keys needed)
- ✅ LLM responses (Gemini)
- ✅ Inventory tool
- ✅ Reminder tool
- ✅ TTS synthesis (ElevenLabs) - will work in audio mode

## ❌ What Needs Setup

- ❌ STT (AssemblyAI) - Get free key at https://www.assemblyai.com/

## 🎯 Quick Test Now

Run this:
```bash
python agent.py console
```

Then type:
```
Namaste
```

You should see the agent respond in Hindi!

## 🐛 Troubleshooting

**"Agent doesn't respond"**
- Make sure you're in Text mode (default)
- Press Enter after typing
- Check that Gemini API key is in .env.local

**"Audio mode not working"**
- You need ASSEMBLYAI_API_KEY in .env.local
- Switch back to Text mode with Ctrl+B

**"Agent crashed"**
- Check .env.local has GOOGLE_API_KEY and ELEVENLABS_API_KEY
- Run `python agent.py download-files` again
- Check terminal output for specific errors

## 📊 Next Steps

1. **Test text mode now** (works immediately!)
2. Get AssemblyAI key for audio mode (5 min signup)
3. Test audio mode
4. Try inventory management
5. Try reminders
6. Deploy to production

Enjoy! 🚀
