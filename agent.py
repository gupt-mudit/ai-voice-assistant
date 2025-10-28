"""
LiveKit Voice Agent for Shopkeepers
Main entry point for the voice assistant agent
"""
import asyncio
import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero, deepgram, elevenlabs, google, cartesia
# Uncomment these when you have the plugins installed:
# from livekit.plugins import noise_cancellation
# from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import your agent
from agents.shopkeeper_agent import ShopkeeperAgent

# Load environment variables
load_dotenv(".env.local")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("shopkeeper-agent")

# Reduce noise from other loggers
logging.getLogger("livekit").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def prewarm(proc: JobProcess):
    """
    Prewarm function to load models before agent starts
    This improves first-response latency
    """
    logger.info("🔥 Prewarming models...")
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD model loaded")


async def entrypoint(ctx: JobContext):
    """
    Main entry point when a user connects to the agent
    This is called for each new session
    """
    logger.info(f"🎤 New session started in room: {ctx.room.name}")
    
    # Set log context
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    try:
        # Create agent session with your AI providers (hybrid approach)
        session = AgentSession(
            # Speech-to-Text: Deepgram via direct plugin (auto-detects language)
            stt=deepgram.STT(model="nova-2-general", language="hi"),
            
            # LLM: Google Gemini via LiveKit gateway (this will work with your API key)
            llm="google/gemini-2.0-flash",
            
            # TTS: Cartesia - fast and reliable for real-time streaming
            tts=cartesia.TTS(voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),  # Neutral American voice
            
            # Voice Activity Detection (from prewarm)
            vad=ctx.proc.userdata.get("vad"),
            
            # Turn detection for natural conversations
            # Uncomment when plugin is installed:
            # turn_detection=MultilingualModel(),
            
            # Start processing while user is still speaking
            preemptive_generation=True,
            
            # Allow false interruption handling
            resume_false_interruption=True,
            false_interruption_timeout=1.0,
        )
        
        logger.info("✅ Session configured")
        
        # Log all agent messages
        def log_agent_message(msg):
            if hasattr(msg, 'content') and msg.content:
                logger.info(f"🤖 AI says: {msg.content}")
        
        # Start the session with your shopkeeper agent
        await session.start(
            room=ctx.room,
            agent=ShopkeeperAgent(),
            room_input_options=RoomInputOptions(
                # Enable noise cancellation for better audio quality
                # Uncomment when plugin is installed:
                # noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        
        logger.info("🏪 Shopkeeper agent active and ready!")
        
    except Exception as e:
        logger.error(f"❌ Error starting session: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    """
    Run the agent with different modes:
    
    Development:
        python livekit_agent.py dev
        (Connects to LiveKit Cloud for testing)
    
    Console (Python only):
        python livekit_agent.py console
        (Run in terminal with audio I/O)
    
    Production:
        python livekit_agent.py start
        (Production mode)
    
    Download model files:
        python livekit_agent.py download-files
        (Downloads VAD and other model files)
    """
    logger.info("🚀 Starting Shopkeeper Voice Agent...")
    logger.info("="*50)
    logger.info("Agent: Shopkeeper Assistant")
    logger.info("Languages: Hindi + English")
    logger.info("Features: Inventory, Reminders, Billing")
    logger.info("="*50)
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
