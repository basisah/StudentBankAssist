# This module contains the logic for determining when to escalate a conversation to a human agent based
# on certain trigger phrases in the user's input or low-confidence responses from the bot.

# Words thats trigger escalation when mentioned in user input, 
# indicating they want to speak to a human or have a serious issue
triggers = ["speak to someone", "human agent", "representative",
    "complaint", "fraud", "lost card", "stolen", "emergency",
    "wrong charge", "dispute", "can't login", "locked out",
    "talk to a person", "real person", "supervisor",
    "manager", "escalate", "lawyer", "legal",
    "unauthorized", "suspicious", "hacked", "compromised",
    "identity theft", "phishing", "scam",
    "close my account", "cancel my account",
    "file a complaint", "ombudsman", "lost my card", "stolen card",
    "not resolved", "unresolved", "still waiting",
    "overdraft", "overcharged", "double charged",
    "wire fraud", "etransfer fraud", "e-transfer fraud", "account takeover", "account compromise",
    "account hacked", "account phished", "account scammed", "account identity theft", "account unauthorized", "account suspicious", "account fraud",
    "card fraud", "card hacked", "card phished", "card scammed", "card identity theft", "card unauthorized", "card suspicious",
    "transaction fraud", "transaction hacked", "transaction phished", "transaction scammed", "transaction identity theft", "transaction unauthorized", "transaction suspicious",
    "customer service", "customer support", "help", "assist", "assistance",
    "problem", "issue", "concern", "question", "inquiry",
    "confused", "don't understand", "need clarification",
    "not sure", "uncertain", "unsure", "unaware", "unknown"]

# Phrases that indicate the bot's response was low-confidence
uncerstain_phrases = [
    "i don't know", "i cannot answer", "not sure", "unclear", "speak to agent", 
    "human agent", "representative", "i'm not certain", 
    "i don't have enough information",
    "outside my scope", "unable to determine",
    "i cannot provide", "beyond my capabilities",
    "please contact", "recommend reaching out"]

def should_escalate(user_input: str, bot_response: str) -> bool:
    """
    Determine if the conversation should be escalated to a human agent.
    
    Checks for:
        1. Trigger keywords in the user's message
        2. Low-confidence phrases in the bot's response
    
    Args:
        user_input (str): The user's input message.
        bot_response (str): The bot's generated response.
    
    Returns:
        bool: True if escalation is needed, False otherwise.
    """

    msg = user_input.lower()
    resp = bot_response.lower()

    for trigger in triggers:
        if trigger in msg:
            return True
    for phrase in uncerstain_phrases:
        if phrase in resp:
            return True
    
    return False
