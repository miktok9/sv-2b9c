"""
Generate 600 Portuguese topics about ancient women's history.
"""

import requests
from urllib.parse import quote
from pathlib import Path
import time

import os
from dotenv import load_dotenv
load_dotenv()

def generate_swedish_topics_batch(batch_num, count=100):
    """Generate a batch of Swedish topics using paid Pollinations API."""
    
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY environment variable is required")

    system = (
        "Du är en historiker som specialiserar dig på kvinnors historia i antika civilisationer. "
        f"Skapa {count} unika ämnen på svenska. "
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
    
    print(f"[batch {batch_num}] Generating {count} Swedish topics...")
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        
        data = r.json()
        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"]["content"].strip()
        else:
            text = r.text.strip()

        # Parse topics
        topics = []
        for line in text.split('\n'):
            cleaned = line.strip()
            # Remove common prefixes
            for prefix in ['- ', '* ', '• ', '→ ', '> ']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):]
            # Remove numbering
            import re
            cleaned = re.sub(r'^\d+[\.\:\)\-]\s*', '', cleaned)
            
            if cleaned and len(cleaned) > 5:
                topics.append(cleaned)
        
        print(f"[batch {batch_num}] Generated {len(topics)} topics")
        return topics[:count]
    
    except Exception as e:
        print(f"[batch {batch_num}] Error: {e}")
        return []

def main():
    """Generate 600 Swedish topics in batches."""
    
    all_topics = []
    batches = 6  # 6 batches of 100 = 600 topics
    
    for i in range(batches):
        topics = generate_swedish_topics_batch(i+1, 100)
        all_topics.extend(topics)
        
        print(f"[progress] Total topics so far: {len(all_topics)}")
        
        # Wait between batches to avoid rate limits
        if i < batches - 1:
            print("[progress] Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    # Write to file
    topics_file = Path('topics.txt')
    with open(topics_file, 'w', encoding='utf-8') as f:
        for topic in all_topics:
            f.write(f"{topic}\n")
    
    print(f"\n[done] Generated {len(all_topics)} Swedish topics!")
    print(f"[done] Saved to {topics_file}")

if __name__ == '__main__':
    main()
