import ollama
import json
from typing import Optional, List, Dict, Any

# ==============================
# NEGOTIATION RESPONSE
# ==============================
class NegotiationResponse:
    """A structured class to hold the agent's response."""
    def __init__(self, action: str, message: str, offer_price: Optional[int] = None):
        self.action = action
        self.message = message
        self.offer_price = offer_price

    def __repr__(self):
        return f"<NegotiationResponse action={self.action} message='{self.message}' price={self.offer_price}>"

# ==============================
# BUYER AGENT CLASS
# ==============================
class BuyerAgent:
    """
    An agent that uses a local LLM via Ollama to negotiate purchases.
    """
    def __init__(self, product: str, budget: int):
        self.product = product
        self.budget = budget
        self.negotiation_history: List[Dict[str, Any]] = []
        self.round_number = 0
        self.last_agent_offer: Optional[int] = None
        print(f"New BuyerAgent created for {product} with a budget of ₹{budget}")

    def negotiate(self, seller_offer: int) -> NegotiationResponse:
        """
        Takes a seller's offer and returns a negotiation response.
        """
        self.round_number += 1
        self.negotiation_history.append({'round': self.round_number, 'speaker': 'seller', 'offer': seller_offer})

        prompt = self._build_prompt(seller_offer)

        try:
            # Call the Ollama API
            response = ollama.chat(
                model='phi3',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.2}, # Lower temperature for more strategic, less random responses
                format='json'
            )
            
            response_text = response['message']['content']
            response_data = json.loads(response_text)
            
            action = response_data.get("action", "error").lower()
            message = response_data.get("message", "I am not sure how to respond.")
            offer_price = response_data.get("offer_price")

            # Update agent's state based on the action
            if action == "counter" and offer_price is not None:
                self.last_agent_offer = offer_price

            self.negotiation_history.append({
                'round': self.round_number,
                'speaker': 'agent',
                'action': action,
                'message': message,
                'offer': offer_price
            })

            return NegotiationResponse(
                action=action,
                message=message,
                offer_price=offer_price
            )

        except Exception as e:
            print(f"An error occurred while calling Ollama or parsing the response: {e}")
            return NegotiationResponse(
                action="error",
                message=f"Sorry, I encountered a system error: {e}",
                offer_price=None
            )

    def _build_prompt(self, current_seller_offer: int) -> str:
        """Helper method to construct the prompt for the LLM with an enhanced strategy."""
        
        history_str = json.dumps(self.negotiation_history, indent=2)
        
        prompt = f"""
        You are a master negotiation agent for a buyer. You are rational, strategic, and polite. Your goal is to purchase a "{self.product}" for the best possible price, never exceeding your absolute maximum budget of ₹{self.budget}.

        **Current Situation:**
        - **Round:** {self.round_number}
        - **Your Maximum Budget:** ₹{self.budget}
        - **Seller's Current Offer:** ₹{current_seller_offer}
        - **Your Previous Offer:** {f"₹{self.last_agent_offer}" if self.last_agent_offer else "You have not made an offer yet."}
        - **Negotiation History (JSON):**
          {history_str}

        **Hard Rules (MUST FOLLOW):**
        - **NEVER** exceed the maximum budget of ₹{self.budget}. Any offer you make or accept must be less than or equal to this amount.
        - Your response **MUST** be in the specified JSON format.

        **Your Negotiation Strategy:**
        1.  **Opening Offer (Round 1):** If you haven't made an offer yet, your first counter-offer should be aggressive to anchor the negotiation low. A good starting point is around 80-90% of the seller's first offer, but well below your budget.
        2.  **Making Concessions:** In subsequent rounds, if you make a new counter-offer, it must be a calculated concession. It must be HIGHER than your last offer ({self.last_agent_offer}) but remain LOWER than the seller's current offer ({current_seller_offer}). Concessions should be small to show you are nearing your limit.
        3.  **Evaluating Offers:** Do not accept an offer just because it is below your budget. Your goal is maximum savings. Only accept if the seller has made a significant concession and the price is a clear value.
        4.  **Budget Adherence:** If the seller's offer is above budget, you must reject or counter with a price at or below your budget. Do not even consider accepting it.
        5.  **Final Offer:** After 3-4 rounds of back-and-forth, you can signal that you are making your "best and final offer" to create urgency.
        6.  **Justify Your Offers:** Briefly justify your offers with polite reasons (e.g., "based on market value," "at the top of my budget," etc.).

        **Your Task:**
        Analyze the current situation and history. Decide on one of three actions: "accept", "reject", or "counter".
        
        You MUST respond in a valid JSON format with three keys:
        - "action": A string, must be exactly "accept", "reject", or "counter".
        - "message": A short, polite string to the seller explaining your decision and reasoning.
        - "offer_price": An integer representing your new offer price if your action is "counter", or the accepted price if "accept". This value **MUST NOT** exceed your budget of ₹{self.budget}. This should be null if you "reject".

        Example for Round 1 (Seller offers ₹28000, Budget ₹25000):
        {{
            "action": "counter",
            "message": "Thank you for the offer. That's a bit more than I was expecting to pay. Based on my research, I can start with an offer of ₹23000.",
            "offer_price": 23000
        }}

        Example for a subsequent round (Your last offer was ₹24000, Seller offers ₹25500, Budget ₹25000):
        {{
            "action": "counter",
            "message": "We're getting closer. I can raise my offer to ₹24500. That would be my absolute maximum.",
            "offer_price": 24500
        }}

        Now, provide your JSON response for the seller's current offer of ₹{current_seller_offer}.
        """
        return prompt
