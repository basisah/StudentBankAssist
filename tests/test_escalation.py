# tests/test_escalation.py
import pytest
from chat.escalation import should_escalate, triggers as TRIGGERS, uncerstain_phrases as UNCERTAIN_PHRASES


# ========== Trigger keyword tests ==========

def test_escalate_on_fraud():
    assert should_escalate("I think there is fraud on my account", "Let me help.") is True


def test_escalate_on_lost_card():
    assert should_escalate("I lost my card", "Let me help.") is True


def test_escalate_on_human_agent():
    assert should_escalate("I want to speak to a human agent", "Sure.") is True


def test_escalate_on_complaint():
    assert should_escalate("I want to file a complaint", "Sure.") is True


def test_escalate_on_identity_theft():
    assert should_escalate("Someone stole my identity theft", "Let me help.") is True


def test_escalate_on_close_account():
    assert should_escalate("I want to close my account", "Sure.") is True


def test_escalate_on_locked_out():
    assert should_escalate("I can't login to my account", "Let me help.") is True


def test_escalate_case_insensitive():
    """Triggers should work regardless of capitalization"""
    assert should_escalate("FRAUD on my account!", "Okay.") is True
    assert should_escalate("I Want A REPRESENTATIVE", "Sure.") is True


# ========== Uncertain response tests ==========

def test_escalate_on_uncertain_response():
    assert should_escalate("What is my balance?", "I don't know your balance.") is True


def test_escalate_on_bot_saying_contact():
    assert should_escalate("Help me", "Please contact RBC directly.") is True


def test_escalate_on_outside_scope():
    assert should_escalate("Can you do this?", "This is outside my scope.") is True


def test_escalate_on_cannot_provide():
    assert should_escalate("Give me details", "I cannot provide that information.") is True


# ========== No escalation tests ==========

def test_no_escalate_on_normal_question():
    assert should_escalate("What is a TFSA?", "A TFSA is a tax-free savings account.") is False


def test_no_escalate_on_greeting():
    assert should_escalate("Hello", "Hi! How can I help you today?") is False


def test_no_escalate_on_product_question():
    assert should_escalate("Tell me about chequing accounts", "RBC offers several chequing accounts.") is False


# ========== Data validation tests ==========

def test_triggers_not_empty():
    assert len(TRIGGERS) > 0


def test_uncertain_phrases_not_empty():
    assert len(UNCERTAIN_PHRASES) > 0


def test_all_triggers_are_lowercase():
    """Ensures trigger matching works since we lowercase the input"""
    for trigger in TRIGGERS:
        assert trigger == trigger.lower(), f"Trigger not lowercase: {trigger}"


def test_all_uncertain_phrases_are_lowercase():
    for phrase in UNCERTAIN_PHRASES:
        assert phrase == phrase.lower(), f"Phrase not lowercase: {phrase}"

