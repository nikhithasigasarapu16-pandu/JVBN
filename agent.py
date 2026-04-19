# agent.py
# The AI brain - talks to Groq and uses memory

import os
from groq import Groq
from memory import save_memory, search_memory
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert incident response agent for a software engineering team.
Your job is to:
1. Analyze incoming incidents (errors, outages, crashes)
2. Use past incident memory to find similar problems and their solutions
3. Suggest a clear step-by-step resolution plan
4. Learn from every incident you resolve

Always be direct, technical, and fast. Lives (and uptime) depend on you."""


def analyze_incident(incident_description):
    """Takes an incident description and returns AI analysis + fix suggestions."""

    # Step 1: Search memory for similar past incidents
    print("\n[Searching memory for similar past incidents...]\n")
    past_memory = search_memory(incident_description)

    # Step 2: Build the message with memory context
    if past_memory:
        user_message = f"""
NEW INCIDENT:
{incident_description}

RELEVANT PAST INCIDENTS FROM MEMORY:
{past_memory}

Based on the past incidents above, diagnose this new incident and provide:
1. Most likely root cause
2. Step-by-step resolution (be specific, use exact commands if possible)
3. How long it might take to fix
4. How to prevent it from happening again
"""
    else:
        user_message = f"""
NEW INCIDENT:
{incident_description}

No similar past incidents found in memory. Please diagnose and provide:
1. Most likely root cause
2. Step-by-step resolution
3. Estimated time to fix
4. Prevention steps
"""

    # Step 3: Call Groq AI
    print("[Asking AI to analyze...]\n")
    response = client.chat.completions.create(
        model="qwen/qwen3-32b",  # FIX: corrected model name from "qwen-qwen3-32b"
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    answer = response.choices[0].message.content

    # Step 4: Save this incident to memory for future use
    save_memory(incident_description, answer)

    return answer