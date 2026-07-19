"""
Script to list all available Gemini models for the current API key
that support generateContent (i.e., can be used for vision/chat).
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print(f"Using API key: {api_key[:20]}...")
print("=" * 60)
print("Models that support generateContent:")
print("=" * 60)

vision_models = []

for model in client.models.list():
    supported = getattr(model, "supported_actions", None) or getattr(model, "supported_generation_methods", [])
    supports_generate = any("generateContent" in str(a) for a in supported)
    
    if supports_generate:
        print(f"  NAME: {model.name}")
        print(f"  DISPLAY: {getattr(model, 'display_name', 'N/A')}")
        print(f"  INPUT TYPES: {getattr(model, 'supported_actions', 'N/A')}")
        print()
        vision_models.append(model.name)

print("=" * 60)
print(f"Total generateContent models found: {len(vision_models)}")
print("=" * 60)
print("Full list:", vision_models)
