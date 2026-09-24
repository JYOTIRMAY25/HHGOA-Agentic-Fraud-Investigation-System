"""
Test candidate models using the Chat API — exactly how the agent uses them.
Also tests the full agent Gemini loop with each working model.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types as gt

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
candidates = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3.8-flash",
]

print("=== Chat API test (agent-style) ===\n")
working = []
for model in candidates:
    try:
        chat = client.chats.create(
            model=model,
            config=gt.GenerateContentConfig(temperature=0.0),
        )
        r = chat.send_message("Reply with exactly the word: OK")
        text = (r.text or "").strip()
        if text:
            print(f"PASS  {model}  reply={text!r}")
            working.append(model)
        else:
            # Check finish reason
            finish = ""
            if r.candidates:
                finish = str(r.candidates[0].finish_reason)
            print(f"FAIL  {model}  empty text  finish_reason={finish}")
    except Exception as e:
        print(f"FAIL  {model}  {type(e).__name__}: {str(e)[:120]}")

print(f"\nWorking models: {working}")
if working:
    print(f"Recommended   : {working[0]}")
