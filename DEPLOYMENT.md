# Railway Deployment Guide

1. **Install dependencies locally**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. **Collect static files (optional locally, required in CI/CD)**
   ```powershell
   python manage.py collectstatic --noinput
   ```
3. **Push the repo to GitHub**
   - `git init` (if needed), create a repo, add remote, push `main` branch.
4. **Create a project on Railway**
   - Select "Deploy from GitHub" and choose this repository.
   - Railway will detect the `railway.toml` file and use Nixpacks with the commands defined there.
5. **Provision a PostgreSQL database**
   - Add the PostgreSQL plugin or existing database and copy the `DATABASE_URL` variable set by Railway.
6. **Configure environment variables** using the `.env.example` template:
   - `DJANGO_SECRET_KEY`: generate via `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.
   - `DJANGO_DEBUG`: set to `False` in production.
   - `DJANGO_ALLOWED_HOSTS`: comma separated hostnames (e.g., `your-custom-domain.com,.railway.app`).
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: include your Railway domain `https://*.railway.app` plus custom domains.
   - Leave `DATABASE_URL` as provided by Railway.
7. **Deploy**
   - On build, Railway runs `python manage.py collectstatic --noinput` (via `railway.toml`).
   - On each deployment, the start command runs `python manage.py migrate && gunicorn spass.wsgi --log-file -`.
8. **Post-deploy checks**
   - Visit the Railway-provided domain to verify.
   - Tail logs via the Railway dashboard if issues appear.

## Helpful local commands
- `python manage.py check --deploy`
- `python manage.py migrate`
- `python manage.py createsuperuser`

