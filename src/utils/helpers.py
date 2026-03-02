import tldextract
import re
import math

def extract_domain(url: str) -> str:
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"

def is_shortened_url(url: str) -> bool:
    short_domains = {'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly'}
    domain = extract_domain(url)
    return domain in short_domains

def calculate_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    entropy = -sum((count / len(text)) * math.log2(count / len(text)) for count in freq.values())
    return entropy