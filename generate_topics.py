"""
Generate new topics using AI when topics.txt runs low.

This script:
1. Checks if topics.txt has enough topics (< 50 remaining)
2. Generates 100 new unique topics using Pollinations AI paid API
3. Appends them to topics.txt
"""

import os
import requests
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_new_topics(count=100):
    """Generate new Swedish topics about ancient women using paid Pollinations API."""

    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY environment variable is required for paid API")

    system = (
        "Du är en historiker som specialiserar dig på kvinnors historia i antika civilisationer. "
        f"{count} unika ämnen på svenska. "
        "Varje ämne ska vara kort (5-10 ord), intressant och utbildande. "
        "Ämnena ska täcka: lagar, sedvänjor, kända kvinnor, yrken, religion, kultur, konst. "
        "SKRIV BARA ämnena, en per rad, utan nummer eller tecken."
    )

    prompt = f"Skapa {count} unika ämnen om kvinnor i antika civilisationer"

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9
    }

    print(f"[topics] Generating {count} new topics...")
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    
    # Parse standard chat completions response
    data = r.json()
    if "choices" in data and len(data["choices"]) > 0:
        text = data["choices"][0]["message"]["content"].strip()
    else:
        # Fallback
        text = r.text.strip()
    
    # Parse topics
    topics = []
    for line in text.split('\n'):
        # Remove numbering and clean
        cleaned = line.strip()
        # Remove common prefixes
        for prefix in ['- ', '* ', '• ']:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        # Remove numbering like "1. " or "1) "
        import re
        cleaned = re.sub(r'^\d+[\.\:\)]\s*', '', cleaned)
        
        if cleaned and len(cleaned) > 5:
            topics.append(cleaned)
    
    return topics[:count]

def check_and_update_topics():
    """Check topics.txt and add more if needed."""
    
    topics_file = Path('topics.txt')
    
    # Read existing topics
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    else:
        existing_topics = []
    
    print(f"[topics] Current topics: {len(existing_topics)}")
    
    # Check if we need more topics
    if len(existing_topics) < 50:
        print(f"[topics] Low on topics! Generating 100 more...")
        
        new_topics = generate_new_topics(100)
        
        # Append to file
        with open(topics_file, 'a', encoding='utf-8') as f:
            for topic in new_topics:
                f.write(f"{topic}\n")
        
        print(f"[topics] Added {len(new_topics)} new topics!")
        print(f"[topics] Total topics now: {len(existing_topics) + len(new_topics)}")
    else:
        print(f"[topics] Enough topics available ({len(existing_topics)})")

if __name__ == '__main__':
    check_and_update_topics()
