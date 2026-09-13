# FlaskProjects

A collection of small Flask applications. The current project is **Shortly**, a local-first URL shortener with authentication and a polished responsive interface.

## Shortly

Shortly lets users create shareable short links, sign in securely, and browse their personal link history. Data is stored in a local SQLite database, so the project runs without any external services.

### Features

- User registration and login with securely hashed passwords
- Authenticated URL shortening for `http://` and `https://` links
- Shareable redirect routes and one-click copy
- Per-user link history
- Automatic local SQLite database initialization
- Responsive frontend built with plain HTML and CSS

### Run locally

```powershell
cd URLShortner
.\Scripts\Activate.ps1  # optional: use your existing virtual environment
pip install -r requirements.txt
$env:SECRET_KEY = "replace-this-in-development"
python app.py
```

Open <http://127.0.0.1:8080> in your browser and create an account.

The database is created at `URLShortner/instance/shortener.sqlite3` on first run. Set `DATABASE_PATH` to use another SQLite file.

### Project structure

```text
URLShortner/
├── app.py
├── models/database.py
├── templates/
├── static/css/main.css
└── requirements.txt
```

### Security notes

Use a long, random `SECRET_KEY` in any shared or production environment. SQLite is a good local development database; use a managed database before deploying publicly.
