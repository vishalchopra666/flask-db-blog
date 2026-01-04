from flask import Blueprint, render_template, abort, request, Response, url_for
from app.models import Post
from app.models import Category, Tag
from .utils import cache_file
from datetime import datetime
from app.admin.utils import get_setting
from app.admin.utils import is_cache_enabled
import os


blog_bp = Blueprint("blog", __name__)

@blog_bp.route("/")
def home():
    cache_path = cache_file()

    # Serve from cache if exists
    if is_cache_enabled() and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    page = request.args.get("page", 1, type=int)

    pagination = (
        Post.query
        .filter_by(status="published")
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=int(get_setting("posts_per_page", 5)), error_out=False)
    )

    html = render_template(
        "blog/home.html",
        posts=pagination.items,
        pagination=pagination,
        seo_title=get_setting("site_title", "My Blog"),
        seo_description=None,
        canonical_url=request.base_url,
        noindex=True if page > 1 else False
    )

    # Save to cache
    if is_cache_enabled():
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html


@blog_bp.route("/category/<slug>")
def category_page(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = [p for p in category.posts if p.status == "published"]
    return render_template(
        "blog/category.html",
        category=category,
        posts=posts,
        seo_title=f"{category.name} Articles",
        seo_description=None,
        canonical_url=request.url,
        noindex=True
    )


@blog_bp.route("/tag/<slug>")
def tag_page(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    posts = [p for p in tag.posts if p.status == "published"]
    return render_template(
        "blog/tag.html",
        tag=tag,
        posts=posts,
        seo_title=f"Posts tagged {tag.name}",
        seo_description=None,
        canonical_url=request.url,
        noindex=True
    )

@blog_bp.route("/sitemap.xml")
def sitemap():
    pages = []

    # Homepage
    pages.append({
        "loc": url_for("blog.home", _external=True),
        "lastmod": datetime.utcnow().date().isoformat()
    })

    # Published posts (indexable only)
    posts = Post.query.filter_by(status="published", noindex=False).all()
    for post in posts:
        pages.append({
            "loc": url_for("blog.post_detail", slug=post.slug, _external=True),
            "lastmod": post.updated_at.date().isoformat()
        })

    xml = render_template("blog/sitemap.xml", pages=pages)
    return Response(xml, mimetype="application/xml")

@blog_bp.route("/robots.txt")
def robots():
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /category/
Disallow: /tag/

Sitemap: {sitemap}
""".format(
        sitemap=url_for("blog.sitemap", _external=True)
    )

    return Response(content, mimetype="text/plain")


@blog_bp.route("/<slug>")
def post_detail(slug):
    cache_path = cache_file()
    comments_embed=get_setting("comments_embed", "")

    if is_cache_enabled() and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    post = Post.query.filter_by(slug=slug, status="published").first()
    if not post:
        abort(404)

    html = render_template(
            "blog/post.html",
            post=post,
            seo_title=post.meta_title or post.title,
            seo_description=post.meta_description,
            canonical_url=post.canonical_url or request.url,
            noindex=post.noindex,
            comments_embed=get_setting("comments_embed", "")
        )


    if is_cache_enabled():
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html
