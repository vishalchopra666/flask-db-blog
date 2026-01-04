from datetime import datetime
from .extensions import db

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"))
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Setting {self.key}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="draft")

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", backref="posts")

    tags = db.relationship("Tag", secondary=post_tags, backref="posts")

    # Images
    featured_image = db.Column(db.String(255))
    featured_image_external = db.Column(db.String(500))
    image_alt = db.Column(db.String(255))

    # SEO
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    noindex = db.Column(db.Boolean, default=False)
    canonical_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Post {self.title}>"

