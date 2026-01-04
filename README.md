# flask-db-blog

# Flask Blog (Minimal CMS)

A **minimal, fast, and SEO-friendly blog CMS** built with Flask.  
Designed intentionally for **content publishing**, not as a heavy SaaS.

This project focuses on:
- Simplicity
- Performance
- Full control
- Low hosting cost

---

## ✨ Features

- Admin dashboard (protected)
- Post create / edit / publish / draft
- SEO controls (meta title, description, canonical, noindex)
- Custom slugs
- Categories
- Media manager (upload / delete)
- Third-party comments embed (Disqus, Giscus, etc.)
- Disk HTML caching (always on by design)
- Responsive admin UI (Bootstrap)
- Clean URLs (no `/post/` prefix)

---

## 📁 Project Structure

Flask Blog/
│
├── app/
│ ├── admin/ # Admin panel (routes, utils, templates)
│ ├── blog/ # Public blog routes
│ ├── models.py # Database models
│ ├── templates/ # Jinja templates
│ ├── static/
│ │ └── uploads/ # Media uploads (ignored by git)
│
├── cache/ # HTML cache (ignored by git)
├── instance/ # Database lives here (ignored by git)
│
├── config.py
├── run.py
└── README.md



---

## ⚙️ Requirements

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- python-slugify

Install dependencies:

```bash
pip install flask flask-sqlalchemy python-slugify


🔐 Environment Variables

Set these before running the app:

SECRET_KEY=your-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=strongpassword

(Do not commit these to GitHub.)

▶️ Run the App
python run.py


Then open:

Blog: http://127.0.0.1:5000

Admin: http://127.0.0.1:5000/admin

🛡️ Security Notes

Admin credentials are stored in environment variables (not DB)

Admin routes are protected

CSRF protection added for admin forms

File uploads are restricted and sanitized

Admin pages are marked noindex, nofollow

This setup is sufficient and appropriate for a blog.

🚀 Deployment Notes

Works well on shared hosting or low-cost VPS

Disk cache keeps hosting cost low

Compatible with Cloudflare CDN

Database auto-creates on first run

📌 Philosophy

This project intentionally avoids:

User accounts

Complex permissions

Analytics bloat

Feature creep

It is built to publish content fast and reliably.

📄 License

MIT — use it, modify it, learn from it.


---

### You’re done ✅

This README:
- Explains purpose clearly
- Matches your architecture
- Is GitHub-ready
- Sets correct expectations

You can now **stop coding and start writing content** 👌

