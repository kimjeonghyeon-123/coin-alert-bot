# trusted_patterns.py
import json
import os

TRUSTED_PATTERNS_FILE = "trusted_patterns.json"

def load_trusted_patterns():
    if os.path.exists(TRUSTED_PATTERNS_FILE):
        with open(TRUSTED_PATTERNS_FILE, "r") as f:
            return set(json.load(f).keys())
    return set()

def filter_trusted_patterns(patterns):
    trusted = load_trusted_patterns()
    return [p for p in patterns if p in trusted]
