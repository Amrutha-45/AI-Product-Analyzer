"""
Test vision model candidates - ASCII only output for Windows compatibility.
Tests each model individually and catches errors without crashing.
"""
import os, asyncio, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 1x1 white pixel PNG
TINY_PNG = bytes([
    0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0x00,0x00,0x00,0x0d,0x49,0x48,0x44,0x52,
    0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
    0xde,0x00,0x00,0x00,0x0c,0x49,0x44,0x41,0x54,0x08,0xd7,0x63,0xf8,0xff,0xff,0x3f,
    0x00,0x05,0xfe,0x02,0xfe,0xdc,0xcc,0x59,0xe7,0x00,0x00,0x00,0x00,0x49,0x45,0x4e,
    0x44,0xae,0x42,0x60,0x82
])

# Test these candidates from the verified model list
CANDIDATES = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
]

async def test_model(model_id):
    try:
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=[
                types.Part.from_bytes(data=TINY_PNG, mime_type="image/png"),
                "Say the word 'pixel' if you can see an image."
            ],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        text = response.text.strip()[:80] if response.text else "(empty)"
        print(f"  [OK]   {model_id}: '{text}'")
        return model_id
    except Exception as e:
        err = str(e)[:150].replace('\n', ' ')
        print(f"  [FAIL] {model_id}: {err}")
        return None

async def main():
    print("Testing vision candidates...\n")
    working = []
    for model_id in CANDIDATES:
        result = await test_model(model_id)
        if result:
            working.append(result)
        await asyncio.sleep(2)  # avoid triggering rate limits between tests

    print("\n" + "="*60)
    if working:
        print(f"WORKING MODELS: {working}")
        print(f"BEST CHOICE: {working[0]}")
    else:
        print("NO MODELS PASSED. All failed or quota exceeded.")
    print("="*60)

asyncio.run(main())
