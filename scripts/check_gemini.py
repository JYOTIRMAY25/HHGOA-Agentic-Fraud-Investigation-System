"""
Gemini API configuration verifier.
Reads GEMINI_API_KEY from .env — never prints it.
Lists available models, checks generateContent support,
tests the configured model, recommends the best available Flash model.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY", "")
configured_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

print("=== Gemini API Configuration Check ===\n")
print(f"Key present      : {bool(key)}")
print(f"Key length       : {len(key)}")
print(f"Configured model : {configured_model}")
print()

if not key:
    print("RESULT: No GEMINI_API_KEY found in .env — local fallback engine will be used.")
    sys.exit(0)

# ── 1. List available models ──────────────────────────────────────────────
try:
    from google import genai
    client = genai.Client(api_key=key)
    models_page = client.models.list()
    all_models = list(models_page)
except Exception as e:
    print(f"ERROR listing models: {type(e).__name__}: {e}")
    sys.exit(1)

# ── 2. Filter to generateContent-capable models ───────────────────────────
def supports_generate(m) -> bool:
    try:
        actions = getattr(m, "supported_actions", None) or []
        if actions:
            return "generateContent" in actions
        # Fallback: name heuristic
        name = getattr(m, "name", "") or ""
        return "gemini" in name.lower()
    except Exception:
        return False

compatible = [m for m in all_models if supports_generate(m)]
model_names = [getattr(m, "name", str(m)) for m in compatible]

# Strip "models/" prefix for display
def short(name: str) -> str:
    return name.replace("models/", "")

print(f"Total models available : {len(all_models)}")
print(f"generateContent capable: {len(compatible)}")
print()

# ── 3. Flash models specifically ─────────────────────────────────────────
flash_models = [n for n in model_names if "flash" in n.lower()]
print("Flash models available:")
for n in sorted(flash_models):
    print(f"  {short(n)}")
print()

# ── 4. Check configured model ────────────────────────────────────────────
configured_full = configured_model if configured_model.startswith("models/") else f"models/{configured_model}"
configured_available = configured_full in model_names or configured_model in model_names

print(f"Requested model available: {configured_available}  ({configured_model})")
print()

# ── 5. Recommend best Flash model ────────────────────────────────────────
PREFERENCE = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash-latest",
]

recommended = None
for pref in PREFERENCE:
    if any(pref in short(n) for n in model_names):
        recommended = pref
        break

if not recommended and flash_models:
    recommended = short(sorted(flash_models)[-1])

print(f"Recommended model: {recommended or '(none found)'}")
print()

# ── 6. Quick generateContent smoke test ──────────────────────────────────
test_model = configured_model if configured_available else recommended
if not test_model:
    print("RESULT: No suitable model found — local fallback will be used.")
    sys.exit(0)

print(f"Testing model: {test_model}")
try:
    from google.genai import types as gt
    response = client.models.generate_content(
        model=test_model,
        contents="Reply with exactly: OK",
        config=gt.GenerateContentConfig(temperature=0.0, max_output_tokens=8),
    )
    reply = (response.text or "").strip()
    success = bool(reply)
    print(f"Test response    : {reply!r}")
    print(f"Test result      : {'PASS' if success else 'FAIL (empty response)'}")
except Exception as e:
    print(f"Test result      : FAIL — {type(e).__name__}: {e}")
    success = False

print()
print("=== Summary ===")
print(f"Requested model  : {configured_model}")
print(f"Available Flash  : {', '.join(short(n) for n in sorted(flash_models)) or 'none'}")
print(f"Recommended model: {recommended or 'none'}")
print(f"Test result      : {'PASS' if success else 'FAIL — update GEMINI_MODEL in .env'}")
if not configured_available and recommended:
    print(f"\nACTION REQUIRED: Add to .env:")
    print(f"  GEMINI_MODEL={recommended}")
