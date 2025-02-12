from cachetools import TTLCache, cached

ROUGE_PRICE_CACHE = TTLCache(maxsize=50, ttl=1200)