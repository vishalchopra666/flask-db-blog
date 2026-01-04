from flask import Flask, render_template
from .extensions import db
from .admin.routes import admin_bp
from .blog.routes import blog_bp
import secrets

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["CSRF_TOKEN"] = secrets.token_hex(16)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(admin_bp)
    app.register_blueprint(blog_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    return app

