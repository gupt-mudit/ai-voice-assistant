"""
Shopkeeper Agent for LiveKit
This agent handles inventory, reminders, and billing for small shopkeepers
"""
import sys
import os
from typing import Annotated

from livekit.agents import Agent, RunContext
from livekit.agents.llm import function_tool
from pydantic import Field

# Import tools from shopkeeper-assistant/tools directory
from tools.inventory_tool import process_inventory as inventory_process
from tools.reminder_tool import process_reminders as reminder_process


class ShopkeeperAgent(Agent):
    """
    Voice assistant agent for shopkeepers in India
    Helps with inventory management, reminders, and billing
    Speaks both Hindi and English
    """
    
    def __init__(self):
        super().__init__(
            instructions="""
You are a helpful voice assistant for small shopkeepers in India.
You help manage their business with:
- Inventory management (tracking stock, updating quantities)
- Setting reminders for important tasks
- Managing bills and transactions

Important Guidelines:
- Speak naturally in Hindi and English (Hinglish is fine)
- Keep responses concise and clear for voice conversations
- Don't use emojis, asterisks, or special characters
- Always confirm important actions before executing
- Be patient and friendly

When the user talks about:
- Stock, items, quantity, inventory → use process_inventory tool
- Reminders, notes, tasks, yaad → use process_reminders tool
- Bills, payments, transactions → use create_bill tool

Examples:
- "5kg aloo add karo" → process_inventory
- "Kal subah reminder set karo" → process_reminders  
- "Customer ka bill banao" → create_bill
"""
        )
    
    @function_tool
    async def process_inventory(
        self,
        context: RunContext,
        user_prompt: Annotated[str, Field(description="The user's complete request about inventory")]
    ) -> str:
        """
        Handle all inventory-related requests including adding, updating, and querying stock.
        
        This tool manages a knowledge base (KB) of inventory items with quantities and metadata.
        
        Args:
            user_prompt: The user's request about inventory
        
        Examples:
        - "5kg aloo add karo"
        - "Kitna pyaaz hai stock mein?"
        - "3 packets maida kam karo"
        - "Aloo ka price 12 rupees per kg hai"
        - "Tell me all items in stock"
        
        Returns:
            A natural language response confirming the action or providing information
        """
        try:
            # Call existing inventory tool
            result = inventory_process(user_prompt)
            return result
        except Exception as e:
            return f"Sorry, inventory operation failed: {str(e)}"
    
    @function_tool
    async def process_reminders(
        self,
        context: RunContext,
        user_prompt: Annotated[str, Field(description="The user's complete request about reminders or notes")]
    ) -> str:
        """
        Handle reminder and note-taking requests.
        
        This tool manages reminders, to-do items, and notes for the shopkeeper.
        
        Args:
            user_prompt: The user's request about reminders
        
        Examples:
        - "Kal subah 9 baje reminder set karo"
        - "Remind me to order stock on Friday"
        - "Kya reminders hai?"
        - "Complete the payment reminder"
        
        Returns:
            A natural language response confirming the reminder or listing reminders
        """
        try:
            # Call existing reminder tool
            result = reminder_process(user_prompt)
            return result
        except Exception as e:
            return f"Sorry, reminder operation failed: {str(e)}"
    
    @function_tool
    async def create_bill(
        self,
        context: RunContext,
        customer_name: Annotated[str, Field(description="The customer's name")],
        items: Annotated[str, Field(description="List of items with quantities and prices, e.g., '5kg aloo at 60 rupees, 2kg pyaaz at 40 rupees'")]
    ) -> str:
        """
        Create a bill for a customer.
        
        Args:
            customer_name: Name of the customer
            items: Description of items with quantities and prices
        
        Examples:
        - customer_name="Ramesh", items="5kg aloo at 60 rupees, 2kg pyaaz at 40 rupees"
        - customer_name="Priya", items="3 packets maida at 90 rupees"
        
        Returns:
            Bill summary with total amount
        """
        try:
            # Parse items and create bill
            # This is a simple implementation - you can enhance it
            bill_text = f"Bill for {customer_name}\n"
            bill_text += "="*40 + "\n"
            bill_text += f"Items: {items}\n"
            bill_text += "="*40 + "\n"
            
            # You can add more sophisticated billing logic here
            # For now, just return the basic bill
            
            return f"Bill created for {customer_name}. Please check the details."
        except Exception as e:
            return f"Sorry, could not create bill: {str(e)}"
    
    async def on_enter(self):
        """
        Called when the agent session starts
        """
        print("🏪 Shopkeeper Agent: Ready to assist!")
        # Generate initial greeting
        self.session.generate_reply(
            instructions="Greet the shopkeeper in Hindi: Say 'Namaste! Main aapka assistant hoon. Inventory, reminders, ya billing mein kaise madad kar sakta hoon?'"
        )
