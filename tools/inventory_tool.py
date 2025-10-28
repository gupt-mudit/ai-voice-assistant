# inventory_tool_wrapper.py

import os
import json
import logging
import re
import threading
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage
from langchain.tools import tool

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize LLM
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai", temperature=0)

# Knowledge‐base file
KB_FILE = Path("storage/inventory_kb.txt")
PREV_KB_FILE = Path("storage/inventory_kb_prev.txt")

# Ensure storage directory exists
KB_FILE.parent.mkdir(exist_ok=True)

if not KB_FILE.exists():
    KB_FILE.write_text("Last Updated: N/A\nItems:\n(Add items with format: - quantity item (price: X, other details))\n")
    logger.info("Created inventory_kb.txt")


class InventoryLLMResponse(BaseModel):
    kb: str
    response: str
    needs_confirmation: bool = False


def read_kb() -> str:
    """Read the entire knowledge base text."""
    return KB_FILE.read_text()


def write_kb(updated_kb: str):
    """Overwrite the knowledge base with updated text."""
    KB_FILE.write_text(updated_kb)
    logger.info("Updated KB")


def write_kb_with_backup(updated_kb: str):
    """Save previous KB then write the new KB."""
    try:
        prev = read_kb()
    except Exception:
        prev = ""
    try:
        PREV_KB_FILE.write_text(prev)
    except Exception as e:
        logger.warning("Failed to write previous KB backup: %s", e)
    write_kb(updated_kb)


def call_llm(prompt: str) -> str:
    """Invoke the LLM and return its text response."""
    logger.info("LLM prompt: %s", prompt)
    resp = llm.invoke([HumanMessage(content=prompt)])
    text = resp.content if hasattr(resp, "content") else str(resp)
    logger.info("LLM response: %s", text)
    return text.strip()


def extract_json_block(text: str) -> str:
    """Extract a JSON object from the LLM text, tolerating code fences and chatter."""
    # Quick path: valid JSON as-is
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Strip common markdown fences
    if text.strip().startswith("```"):
        lines = text.splitlines()
        while lines and lines[0].strip().startswith("```"):
            lines.pop(0)
        while lines and lines[-1].strip().startswith("```"):
            lines.pop()
        text = "\n".join(lines).strip()

    # Greedy match first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return text


def ensure_kb_header(kb_text: str) -> str:
    """Ensure KB begins with a timestamp header and an Items: line."""
    kb = kb_text.strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not kb.lower().startswith("last updated:"):
        content = kb
        if "Items:" in kb:
            content = kb.split("Items:", 1)[1].lstrip("\n")
        kb = f"Last Updated: {now}\nItems:\n{content}".rstrip()
    else:
        lines = kb.splitlines()
        if lines:
            lines[0] = f"Last Updated: {now}"
        if len(lines) == 1 or not lines[1].strip().lower().startswith("items:"):
            lines.insert(1, "Items:")
        kb = "\n".join(lines)

    return kb


# WRAPPER TOOL - Uses your EXACT inventory_mcp.py logic!
@tool
def process_inventory(user_prompt: str) -> str:
    """
    Process inventory requests using the proven inventory_mcp.py logic.
    Handles multiple operations efficiently in a single LLM call.
    
    Examples:
    - "10kg aloo liya"
    - "add 2kg aloo, tell me how much besan, subtract 3kg onion"
    - "kitna aloo bacha hai"
    - "complete inventory dikhao"
    - "aloo ki price 15 rupay kilo"
    
    Args:
        user_prompt: Natural language inventory request
    
    Returns:
        Response from inventory processing
    """
    # EXACT COPY of your inventory_mcp.py logic!
    
    # 1. Read current KB
    current_kb = read_kb()

    # 2. Build instruction for LLM (your EXACT prompt)
    instruction = f"""
System:
You update a plain-text inventory note for a small shopkeeper. Follow rules strictly:

QUANTITY UPDATES:
- Interpret the user's intent carefully:
  * Phrases like "I have X left" or "X remaining" = set total to X
  * Phrases like "add X" or "bought X more" = add to existing
  * Phrases like "used X" or "sold X" = subtract from existing
  * If completely ambiguous and you cannot determine intent, set needs_confirmation to true

METADATA (prices, suppliers, expiry, etc.):
- Track ALL relevant business information the shopkeeper provides
- Format: "- quantity item (price: X rupees/kg, supplier: Y, expiry: Z, etc.)"
- Examples:
  * "- 11kg potato (price: 12 rupees/kg)"
  * "- 4kg onion (price: 20/kg, supplier: Ram)"
  * "- 3kg sugar (expiry: Dec 2025)"
- Keep it simple and human-readable
- Update existing metadata or add new metadata as user provides information

QUESTIONS:
- If the user asks a question about the inventory, provide a concise answer.

OUTPUT:
- Return ONLY a single JSON object with exactly these keys:
  {{
    "kb": "FULL_UPDATED_KB_TEXT",
    "response": "USER_FACING_RESPONSE",
    "needs_confirmation": false
  }}
- Set needs_confirmation to true ONLY if the intent is genuinely ambiguous and you need clarification.
- Do NOT use markdown code fences or add any extra text.

Current inventory note (KB):
{current_kb}

User prompt:
{user_prompt}

Output:
Return only the JSON object described above. No explanations.
"""
    
    # 3. Call LLM
    raw = call_llm(instruction)

    # 4. Extract JSON robustly
    raw = extract_json_block(raw)

    # 5. Parse and validate JSON schema
    try:
        try:
            result = InventoryLLMResponse.model_validate_json(raw)
        except AttributeError:
            parsed = json.loads(raw)
            result = InventoryLLMResponse(**parsed)
    except Exception as e:
        logger.error("Invalid LLM output: %s", e)
        return "Sorry, I couldn't process that inventory request."

    updated_kb = result.kb
    user_response = result.response
    llm_needs_confirmation = result.needs_confirmation

    # 6. Check if confirmation is needed
    if llm_needs_confirmation:
        return f"{user_response} (Confirmation needed)"

    # 7. Write new KB with backup in background thread (non-blocking)
    def write_in_background():
        try:
            write_kb_with_backup(ensure_kb_header(updated_kb))
            logger.info("✅ KB saved successfully in background")
        except Exception as e:
            logger.error(f"❌ Failed to save KB in background: {e}")
    
    # Start background write thread (daemon=True means it won't block program exit)
    write_thread = threading.Thread(target=write_in_background, daemon=True)
    write_thread.start()

    # 8. Return result immediately (don't wait for KB write)
    return user_response