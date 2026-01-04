
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import check_password_hash
from .utils import admin_required
from app.models import Post
from app.extensions import db
from slugify import slugify
from app.models import Category, Tag
from .utils import clear_cache
from app.admin.utils import get_setting, set_setting
from .utils import save_image, generate_unique_slug
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == current_app.config["ADMIN_USERNAME"]
            and check_password_hash(
                current_app.config["ADMIN_PASSWORD_HASH"], password
            )
        ):
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin.dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("admin/login.html", error=error)


@admin_bp.route("/")
@admin_required
def dashboard():
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status="published").count()
    draft_posts = Post.query.filter_by(status="draft").count()

    recent_posts = (
        Post.query
        .order_by(Post.updated_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        recent_posts=recent_posts
    )



@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))

@admin_bp.route("/posts")
@admin_required
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("admin/posts/list.html", posts=posts)

@admin_bp.route("/posts/new", methods=["GET", "POST"])
@admin_required
def new_post():
    categories = Category.query.all()

    categories = Category.query.all()
    print("CATEGORIES FOUND:", categories)


    if request.method == "POST":
        if request.form.get("csrf_token") != current_app.config["CSRF_TOKEN"]:
            abort(403)
        title = request.form.get("title")
        content = request.form.get("content")
        status = request.form.get("status")
        category_id = request.form.get("category_id")

        image_file = request.files.get("featured_image")
        image_name = save_image(image_file)

        custom_slug = request.form.get("slug")
        slug = generate_unique_slug(
            title=title,
            custom_slug=custom_slug
        )

        post = Post(
            title=title,
            slug=slug,
            content=content,
            status=status,
            category_id=category_id or None,
            meta_title=request.form.get("meta_title"),
            meta_description=request.form.get("meta_description"),
            canonical_url=request.form.get("canonical_url"),
            noindex=True if request.form.get("noindex") else False,
            featured_image=image_name,
            featured_image_external=request.form.get("featured_image_external"),
            image_alt=request.form.get("image_alt")
        )


        db.session.add(post)
        db.session.commit()

        return redirect(url_for("admin.posts"))

    return render_template(
        "admin/posts/form.html",
        post=None,
        categories=categories
    )

@admin_bp.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    categories = Category.query.all()

    if request.method == "POST":
        if request.form.get("csrf_token") != current_app.config["CSRF_TOKEN"]:
            abort(403)

        post.title = request.form.get("title")
        custom_slug = request.form.get("slug")
        post.slug = generate_unique_slug(
            title=post.title,
            custom_slug=custom_slug,
            post_id=post.id
        )
        post.content = request.form.get("content")
        post.status = request.form.get("status")
        post.category_id = request.form.get("category_id") or None

        # SEO
        post.meta_title = request.form.get("meta_title")
        post.meta_description = request.form.get("meta_description")
        post.noindex = True if request.form.get("noindex") else False
        post.canonical_url = request.form.get("canonical_url")

        # Image
        image_file = request.files.get("featured_image")
        image_name = save_image(image_file)

        print("FILES:", request.files)
        print("IMAGE FILE:", image_file)

        if image_name:
            post.featured_image = image_name

        post.featured_image_external = request.form.get("featured_image_external")
        post.image_alt = request.form.get("image_alt")

        db.session.commit()
        return redirect(url_for("admin.posts"))

    return render_template(
        "admin/posts/form.html",
        post=post,
        categories=categories
    )


@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        if request.form.get("csrf_token") != current_app.config["CSRF_TOKEN"]:
            abort(403)
        name = request.form.get("name")
        category = Category(name=name, slug=slugify(name))
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("admin.categories"))

    categories = Category.query.all()
    return render_template("admin/categories.html", categories=categories)

@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Detach posts from this category
    for post in category.posts:
        post.category_id = None

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("admin.categories"))

@admin_bp.route("/tags", methods=["GET", "POST"])
@admin_required
def tags():
    if request.method == "POST":
        if request.form.get("csrf_token") != current_app.config["CSRF_TOKEN"]:
            abort(403)
        name = request.form.get("name")
        tag = Tag(name=name, slug=slugify(name))
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("admin.tags"))

    tags = Tag.query.all()
    return render_template("admin/tags.html", tags=tags)

@admin_bp.route("/cache")
@admin_required
def cache_dashboard():
    cache_dir = os.path.join(current_app.root_path, "cache")
    files = []

    if os.path.exists(cache_dir):
        files = os.listdir(cache_dir)

    return render_template(
        "admin/cache.html",
        cache_count=len(files)
    )


@admin_bp.route("/cache/clear", methods=["POST"])
@admin_required
def clear_cache_route():
    deleted = clear_cache()
    return redirect(url_for("admin.cache_dashboard"))

@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        if request.form.get("csrf_token") != current_app.config["CSRF_TOKEN"]:
            abort(403)
        set_setting("site_title", request.form.get("site_title"))
        set_setting("site_description", request.form.get("site_description"))
        set_setting("posts_per_page", request.form.get("posts_per_page"))
        set_setting("cache_enabled", "1" if request.form.get("cache_enabled") else "0")
        set_setting("comments_embed", request.form.get("comments_embed"))

        return redirect(url_for("admin.settings"))

    return render_template(
        "admin/settings.html",
        site_title=get_setting("site_title", "My Blog"),
        site_description=get_setting("site_description", ""),
        posts_per_page=get_setting("posts_per_page", "5"),
        cache_enabled=get_setting("cache_enabled", "1") == "1",
        comments_embed=get_setting("comments_embed", "")
    )

@admin_bp.route("/media")
@admin_required
def media():
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    files = []

    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                files.append(f)

    files.sort(reverse=True)

    return render_template(
        "admin/media.html",
        files=files
    )

@admin_bp.route("/media/upload", methods=["POST"])
@admin_required
def upload_media():
    file = request.files.get("image")
    save_image(file)
    return redirect(url_for("admin.media"))

@admin_bp.route("/media/<filename>/delete", methods=["POST"])
@admin_required
def delete_media(filename):
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_dir, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("admin.media"))
