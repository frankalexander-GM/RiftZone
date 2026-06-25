import re
import json
import os

_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'profanity_words.json')

def _load_words():
    if os.path.exists(_WORDS_FILE):
        with open(_WORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('words', [])
    return []

_WORDS = _load_words()

if not _WORDS:
    import logging
    logging.getLogger(__name__).warning(
        'profanity_words.json not found or empty at %s', _WORDS_FILE
    )

_PATTERNS = None

def _build_patterns():
    global _PATTERNS
    if _PATTERNS is not None:
        return
    if not _WORDS:
        _PATTERNS = []
        return
    _PATTERNS = [
        re.compile(re.escape(w), re.IGNORECASE)
        for w in sorted(_WORDS, key=len, reverse=True)
    ]

def filter_profanity(text):
    if not text:
        return text
    _build_patterns()
    result = text
    for pattern in _PATTERNS:
        result = pattern.sub(lambda m: '*' * len(m.group()), result)
    return result
