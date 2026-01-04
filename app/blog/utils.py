import os
import hashlib
from flask import request, current_app

def get_cache_path():
    base = os.path.join(current_app.root_path, "cache")
    os.makedirs(base, exist_ok=True)
    return base

def cache_key():
    key = request.full_path.encode("utf-8")
    return hashlib.md5(key).hexdigest() + ".html"

def cache_file():
    return os.path.join(get_cache_path(), cache_key())
