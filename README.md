# social-blog-app
A full-stack Flask web app for blogging. Features include posting, following users, profile editing, and a global explore feed.

Features

- User registration and authentication using Flask-Login
- Create, edit, and delete blog posts
- Follow and unfollow users to personalize your feed
- Paginated feed showing posts from followed users
- Database migrations powered by Flask-Migrate
- Responsive UI styled with Bootstrap
- Secure password hashing via Werkzeug
- Lightweight and fast QLite database for local development

Tech Stack

- ython 3.x
- Flask (web framework)
- Flask-Login (user session management)
- Flask-Migrate (Alembic for database migrations)
- Flask-WTF (form handling and validation)
- SQLAlchemy (ORM for SQLite)
- Bootstrap 4/5 (CSS framework)
- Jinja2 (template engine)
# Clone the repository
git clone https://github.com/Haroon-Nkopa/social-blog-app.git
cd social-blog-app

# Create and activate virtual environment
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
# python -m venv venv
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up the database
flask db upgrade

# Run the development server
flask run

# Open your browser at
# http://127.0.0.1:5000

