#!/usr/bin/env python3
"""Check if system is ready to test with real HuggingFace + Gmail"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("SYSTEM READINESS CHECK")
print("=" * 80)

checks = {
    "EMAIL_USER": os.getenv("EMAIL_USER"),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
    "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
    "HUGGINGFACE_MODEL": os.getenv("HUGGINGFACE_MODEL"),
    "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
}

print("\nCurrent Configuration:")
print("-" * 80)

all_ready = True
for key, value in checks.items():
    if not value:
        status = "✗ MISSING"
        all_ready = False
    elif "xxxx" in str(value) or "hf_" not in str(value) and key == "HUGGINGFACE_API_KEY":
        if key == "EMAIL_PASSWORD" and "xxxx" in str(value):
            status = "⏳ PLACEHOLDER"
            all_ready = False
        elif key == "HUGGINGFACE_API_KEY" and "hf_" not in str(value):
            status = "⏳ PLACEHOLDER"
            all_ready = False
        else:
            status = "✓ SET"
    else:
        status = "✓ SET"
    
    # Mask sensitive values
    display_value = value
    if key in ["EMAIL_PASSWORD", "HUGGINGFACE_API_KEY"] and value:
        if len(value) > 8:
            display_value = value[:8] + "*" * (len(value) - 8)
    
    print(f"  {key:25} {status:15} {display_value}")

print("\n" + "=" * 80)

if all_ready or (os.getenv("LLM_PROVIDER") == "mock"):
    print("✓ SYSTEM READY TO TEST")
    print("=" * 80)
    if os.getenv("LLM_PROVIDER") == "mock":
        print("\nCurrently using MOCK provider (for testing without credentials)")
        print("To test with REAL HuggingFace:")
        print("  1. Get Gmail app password (https://myaccount.google.com/security)")
        print("  2. Get HuggingFace token (https://huggingface.co/settings/tokens)")
        print("  3. Update .env with both values")
        print("  4. Change LLM_PROVIDER=huggingface")
    else:
        print("\nRun this to test:")
        print("  python test_real_email.py")
else:
    print("⏳ WAITING FOR CREDENTIALS")
    print("=" * 80)
    print("\nTo enable real HuggingFace + Gmail testing:")
    
    if EMAIL_PASSWORD := os.getenv("EMAIL_PASSWORD"):
        if "xxxx" in EMAIL_PASSWORD:
            print("  1. [ ] Get Gmail app password")
            print("        https://myaccount.google.com/security")
            print("        Select: Mail + Windows device")
            print("        Copy: 16-char password (xxxx xxxx xxxx xxxx)")
            print("        Add to .env: EMAIL_PASSWORD=xxxx xxxx xxxx xxxx")
    
    if HFKEY := os.getenv("HUGGINGFACE_API_KEY"):
        if "hf_" not in HFKEY:
            print("  2. [ ] Get HuggingFace token")
            print("        https://huggingface.co/settings/tokens")
            print("        Click: New token")
            print("        Copy: hf_xxxxxxxxxxxxx")
            print("        Add to .env: HUGGINGFACE_API_KEY=hf_xxxxx")
    
    print("\n  3. [ ] Change provider in .env:")
    print("        LLM_PROVIDER=huggingface")
    
    print("\n  4. [ ] Run test:")
    print("        python test_real_email.py")

print("\n" + "=" * 80)
