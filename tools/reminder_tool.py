# reminder_tool_wrapper.py

import os
import json
import logging
import re
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

# Reminders file
REMINDERS_FILE = Path("storage/reminders_kb.txt")

# Ensure storage directory exists
REMINDERS_FILE.parent.mkdir(exist_ok=True)

if not REMINDERS_FILE.exists():
    REMINDERS_FILE.write_text("""Last Updated: N/A
Reminders:

URGENT:
(Add urgent reminders here)

DAILY:
(Add daily reminders here)

WEEKLY:
(Add weekly reminders here)

COMPLETED:
(Completed reminders will be moved here)
""")
    logger.info("Created reminders_kb.txt")


class ReminderLLMResponse(BaseModel):
    kb: str
    response: str
    needs_confirmation: bool = False


def read_reminders() -> str:
    """Read the entire reminders knowledge base text."""
    return REMINDERS_FILE.read_text()


def write_reminders(updated_kb: str):
    """Overwrite the reminders knowledge base with updated text."""
    REMINDERS_FILE.write_text(updated_kb)
    logger.info("Updated reminders KB")


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


def ensure_reminders_header(kb_text: str) -> str:
    """Ensure reminders KB begins with a timestamp header."""
    kb = kb_text.strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not kb.lower().startswith("last updated:"):
        content = kb
        if "Reminders:" in kb:
            content = kb.split("Reminders:", 1)[1].lstrip("\n")
        kb = f"Last Updated: {now}\nReminders:\n{content}".rstrip()
    else:
        lines = kb.splitlines()
        if lines:
            lines[0] = f"Last Updated: {now}"
        if len(lines) == 1 or not lines[1].strip().lower().startswith("reminders:"):
            lines.insert(1, "Reminders:")
        kb = "\n".join(lines)

    return kb


# WRAPPER TOOL - Similar to inventory approach
@tool
def process_reminders(user_prompt: str) -> str:
    """
    Process reminder requests using efficient single-prompt logic.
    Handles multiple reminder operations in a single LLM call.
    
    Examples:
    - "kal ko yaad dilana"
    - "reminders dikhao"
    - "urgent reminders dikhao"
    - "reminder complete karo"
    
    Args:
        user_prompt: Natural language reminder request
    
    Returns:
        Response from reminder processing
    """
    # 1. Read current reminders KB
    current_kb = read_reminders()

    # 2. Build instruction for LLM
    instruction = f"""
System:
You manage reminders for a small shopkeeper. Follow rules strictly:

REMINDER MANAGEMENT:
- Add new reminders to appropriate category (URGENT, DAILY, WEEKLY)
- Mark completed reminders by moving them to COMPLETED section
- Update existing reminders if needed
- Categorize reminders based on urgency and frequency

REMINDER FORMAT:
- Use simple, clear language
- Include date/time if specified
- Keep reminders actionable
- Examples:
  * "Restock potato (expires: 2025-10-25)"
  * "Pay electricity bill (due: 2025-10-20)"
  * "Check milk freshness (daily)"
  * "Order new stock (every Monday)"

CATEGORIES:
- URGENT: Time-sensitive, must be done soon
- DAILY: Regular daily tasks
- WEEKLY: Weekly recurring tasks
- COMPLETED: Finished reminders (with completion date)

OUTPUT:
- Return ONLY a single JSON object with exactly these keys:
  {{
    "kb": "FULL_UPDATED_REMINDERS_TEXT",
    "response": "USER_FACING_RESPONSE",
    "needs_confirmation": false
  }}
- Set needs_confirmation to true ONLY if the intent is genuinely ambiguous
- Do NOT use markdown code fences or add any extra text

Current reminders KB:
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
            result = ReminderLLMResponse.model_validate_json(raw)
        except AttributeError:
            parsed = json.loads(raw)
            result = ReminderLLMResponse(**parsed)
    except Exception as e:
        logger.error("Invalid LLM output: %s", e)
        return "Sorry, I couldn't process that reminder request."

    updated_kb = result.kb
    user_response = result.response
    llm_needs_confirmation = result.needs_confirmation

    # 6. Check if confirmation is needed
    if llm_needs_confirmation:
        return f"{user_response} (Confirmation needed)"

    # 7. Write new KB
    write_reminders(ensure_reminders_header(updated_kb))

    # 8. Return result
    return user_response