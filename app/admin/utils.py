from functools import wraps
from flask import session, redirect, url_for, current_app
from app.models import Setting, Post
from app.extensions import db
from slugify import slugify
from werkzeug.utils import secure_filename
import uuid
import os

RESERVED_SLUGS = {
    "admin", "login", "logout",
    "category", "tag", "static",
    "media", "api", "sitemap.xml", "robots.txt"
}

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped_view

def clear_cache():
    cache_dir = os.path.join(current_app.root_path, "cache")
    if not os.path.exists(cache_dir):
        return 0

    count = 0
    for f in os.listdir(cache_dir):
        path = os.path.join(cache_dir, f)
        if os.path.isfile(path):
            os.remove(path)
            count += 1

    return count

def is_cache_enabled():
    return get_setting("cache_enabled", "1") == "1"

def get_setting(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        setting = Setting(key=key)
        db.session.add(setting)
    setting.value = value
    db.session.commit()

def generate_unique_slug(title, custom_slug=None, post_id=None):
    base = custom_slug or title
    slug = slugify(base)

    if slug in RESERVED_SLUGS:
        slug = f"{slug}-post"

    query = Post.query.filter_by(slug=slug)
    if post_id:
        query = query.filter(Post.id != post_id)

    count = query.count()
    if count > 0:
        slug = f"{slug}-{count + 1}"

    return slug

####################### Image Function ##########################

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def save_image(file):
    if not file or file.filename == "":
        return None

    name, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    safe_name = secure_filename(name)
    unique_name = f"{safe_name}-{uuid.uuid4().hex[:8]}{ext}"

    full_path = os.path.join(upload_dir, unique_name)
    file.save(full_path)

    return unique_name
