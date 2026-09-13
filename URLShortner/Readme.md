# Shortly

Shortly is a local-first URL shortener built with Flask. It provides account-based access, hashed passwords, short-link redirects, and a personal link history backed by SQLite.

## Quick start

From this directory:

```powershell
pip install -r requirements.txt
$env:SECRET_KEY = "use-a-random-value"
python app.py
```

Visit <http://127.0.0.1:8080>, create an account, and shorten your first link.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Development fallback | Flask session signing key |
| `DATABASE_PATH` | `instance/shortener.sqlite3` | SQLite database location |
| `PORT` | `8080` | Local web server port |
| `FLASK_DEBUG` | Disabled | Set to `1` only for local debugging |

The database and its tables are created automatically on first start. Passwords are never stored in plain text.
