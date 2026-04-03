"""
Panchayat Bridge — AI Prompt Builder
======================================
Builds system prompts and user prompts for Gemini API calls.
Loads persona data from data/candidates.json and formats it for
LangChain's system_instruction parameter.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_candidates():
    with open(os.path.join(DATA_DIR, "candidates.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def _load_dialogues():
    with open(os.path.join(DATA_DIR, "dialogues.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def get_candidate_system_prompt(candidate_id: str) -> str:
    """
    Get the full system instruction for a candidate.
    This is passed to Gemini's system_instruction parameter to lock the LLM into character.
    """
    data = _load_candidates()
    for c in data["candidates"]:
        if c["id"] == candidate_id:
            return c["system_prompt"]
    raise ValueError(f"Unknown candidate: {candidate_id}")


def get_candidate_info(candidate_id: str) -> dict:
    """Get full candidate info dict."""
    data = _load_candidates()
    for c in data["candidates"]:
        if c["id"] == candidate_id:
            return c
    raise ValueError(f"Unknown candidate: {candidate_id}")


def get_all_candidate_ids() -> list:
    """Return list of all candidate IDs."""
    data = _load_candidates()
    return [c["id"] for c in data["candidates"]]


def build_reaction_prompt(candidate_id: str, player_action: str) -> str:
    """
    Build the user-facing prompt that asks a candidate to react to the player's action.
    The system prompt (persona) is set separately via system_instruction.
    """
    return (
        f"The player (your political opponent) has just announced the following policy:\n\n"
        f"PLAYER'S POLICY: \"{player_action}\"\n\n"
        f"You must react to this policy IN CHARACTER. You have access to tools that let you:\n"
        f"1. Search real-world Indian political scenarios for context\n"
        f"2. Check voter sentiment to understand how this affects your base\n"
        f"3. Analyze how this policy aligns or conflicts with your ideology\n\n"
        f"Use at least ONE tool before responding to ground your reaction in real data.\n\n"
        f"Then give your public reaction in 2-3 sentences, staying completely in character. "
        f"Include your emotional tone and reference specific data from your research."
    )


def build_voter_feed_prompt(voter_group_id: str, player_action: str, candidate_reactions: dict) -> str:
    """
    Build a prompt for generating voter social media reactions.
    Uses Flash model for speed.
    """
    reactions_text = "\n".join(
        f"- {cid}: {reaction}" for cid, reaction in candidate_reactions.items()
    )
    return (
        f"You are simulating social media reactions from the '{voter_group_id}' voter group "
        f"in an Indian Panchayat election.\n\n"
        f"THE PLAYER announced: \"{player_action}\"\n\n"
        f"CANDIDATE REACTIONS:\n{reactions_text}\n\n"
        f"Generate 3 short social media posts (like Twitter/X) from members of this voter group. "
        f"Each post should be 1-2 sentences, authentic, and reflect the group's real concerns. "
        f"Mix Hindi and English naturally. Include emoji."
    )
