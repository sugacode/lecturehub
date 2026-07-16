# Deploying to a VPS (Ubuntu 22.04)

Full root access changes the picture from the shared-hosting guides
(`DEPLOY_HOSTINGER.md`, `DEPLOY_PYTHONANYWHERE.md`): here you run the
standard Django production stack yourself — **gunicorn** (WSGI server) behind
**nginx** (reverse proxy + TLS + static/media serving), supervised by
**systemd**. `whitenoise` (already wired in for the shared-hosting targets)
still works here as a fallback, but nginx serving `/static/` and `/media/`
directly is faster and is what this guide sets up.

**Already running Apache on this box for other sites?** Don't fight it for
port 80 — skip straight to "Alternative: Apache instead of nginx" near the
end, which reverse-proxies through Apache instead.

Commands below assume you're SSH'd in as a non-root sudo user. Replace
`yourdomain.com` and `deploy` (the app-owning user) throughout.

## 1. System packages

Ubuntu 22.04 ships Python 3.10, not 3.12. The `deadsnakes` PPA provides 3.12:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    build-essential libjpeg-dev zlib1g-dev \
    nginx git ufw
```
(`libjpeg-dev`/`zlib1g-dev` are for Pillow's image support — used by the
profile photo upload.)

## 2. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```
Nothing should be listening on the app's own port (8000/unix socket)
directly from the internet — only nginx talks to it.

## 3. Create an app user and get the code

Running the app under its own unprivileged user (not root) is standard
practice:
```bash
sudo adduser --disabled-password --gecos "" deploy
sudo su - deploy
git clone <your-repo-url> ~/lecturerhub
cd ~/lecturerhub
```

## 4. Virtualenv and dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Environment variables

```bash
cp .env.example .env
nano .env
```
Set:
```
DJANGO_SECRET_KEY=<random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=you@example.com
DEFAULT_ADMIN_PASSWORD=<a real password>
```
Leave `SERVE_MEDIA_VIA_DJANGO` unset/`False` — nginx will serve `/media/`
directly (step 8). Leave `DATABASE_URL` unset to keep SQLite, which is
fine for a single-user app on a VPS you control; switch to PostgreSQL
later (see `docs/SETUP_MACOS.md`'s "Switching to PostgreSQL" section) if
you ever need it.

## 6. Migrate, create your account, collect static files

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py create_default_user
python manage.py seed_demo   # optional
python manage.py collectstatic --noinput
```

## 7. gunicorn + systemd

Create `/etc/systemd/system/lecturerhub.service` (as root, so use `sudo
nano` or `exit` back to your sudo user first):

```ini
[Unit]
Description=LecturerHub gunicorn daemon
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/lecturerhub
Environment="DJANGO_SETTINGS_MODULE=config.settings.prod"
ExecStart=/home/deploy/lecturerhub/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/deploy/lecturerhub/lecturerhub.sock \
    config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lecturerhub
sudo systemctl status lecturerhub
```

If it fails to start, `journalctl -u lecturerhub -n 50` shows why (usually
a missing env var or a typo'd path).

## 8. nginx

Create `/etc/nginx/sites-available/lecturerhub`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 12M;  # slightly above MAX_UPLOAD_SIZE_MB (10 MB)

    location /static/ {
        alias /home/deploy/lecturerhub/staticfiles/;
    }

    location /media/ {
        alias /home/deploy/lecturerhub/media/;
    }

    location / {
        proxy_pass http://unix:/home/deploy/lecturerhub/lecturerhub.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/lecturerhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

At this point the site is live over plain HTTP. **Don't set
`DJANGO_SETTINGS_MODULE=config.settings.prod` in production without
HTTPS actually working** — it forces `SECURE_SSL_REDIRECT = True`, which
would redirect-loop until certbot (next step) is done. If you need to
smoke-test over HTTP first, temporarily use `config.settings.dev` for that
one check only.

## 9. HTTPS via certbot (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Certbot edits the nginx config to add the TLS `server` block and set up
auto-renewal (`systemctl status certbot.timer` to confirm the renewal
timer is active).

## Alternative: Apache instead of nginx (server already runs Apache for other sites)

If port 80 is already held by Apache serving other sites on the same box,
don't disable it — add lecturerhub as another Apache vhost reverse-proxying
to gunicorn, instead of introducing nginx to fight for the port. Skip
steps 8–9 above and do this instead.

**Bind gunicorn to a local TCP port instead of a unix socket** (simpler for
Apache's proxy config than `mod_proxy_uds`). In the systemd unit from step
7, change:
```
ExecStart=/home/deploy/lecturerhub/.venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8001 \
    config.wsgi:application
```
```bash
sudo systemctl daemon-reload
sudo systemctl restart lecturerhub
```

**Enable Apache's proxy modules:**
```bash
sudo a2enmod proxy proxy_http headers
```

**Create `/etc/apache2/sites-available/lecturerhub.conf`:**
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    Alias /static/ /home/deploy/lecturerhub/staticfiles/
    Alias /media/  /home/deploy/lecturerhub/media/

    <Directory /home/deploy/lecturerhub/staticfiles>
        Require all granted
    </Directory>
    <Directory /home/deploy/lecturerhub/media>
        Require all granted
    </Directory>

    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://127.0.0.1:8001/
    ProxyPassReverse / http://127.0.0.1:8001/

    RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
```

**Enable the site and reload:**
```bash
sudo a2ensite lecturerhub
sudo apache2ctl configtest
sudo systemctl reload apache2
```

**HTTPS via certbot's Apache plugin:**
```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```
Certbot creates a **new** file, `/etc/apache2/sites-available/<name>-le-ssl.conf`,
for the `<VirtualHost *:443>` block — it copies your `:80` vhost's directives
into it, **including `RequestHeader set X-Forwarded-Proto "http"` verbatim,
unchanged**. It does *not* update that value to `"https"` on its own (despite
what you might expect, or what other guides may claim). Fix it manually or
you'll get an infinite HTTPS redirect loop — Django receives
`X-Forwarded-Proto: http` on every request, including ones that already
arrived over HTTPS, and keeps "correcting" them:

```bash
sudo nano /etc/apache2/sites-available/<name>-le-ssl.conf
```
Change the one line to:
```apache
RequestHeader set X-Forwarded-Proto "https"
```
```bash
sudo apache2ctl configtest
sudo systemctl reload apache2
```

**If the domain is proxied through Cloudflare** (or another CDN/proxy in
front of your VPS), also set its SSL/TLS mode to **Full (strict)**, not
"Flexible" — Flexible mode means Cloudflare talks plain HTTP to your
origin regardless of what the browser used, which independently causes
the same redirect-loop symptom even with the header fixed above.

With this path, `nginx` from step 1's package list is unnecessary; you can
skip installing it, or leave it installed-but-stopped if you already did.

## Updating after a git push

```bash
sudo su - deploy
cd ~/lecturerhub
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit
sudo systemctl restart lecturerhub
```
(nginx doesn't need a restart unless you changed its config.)

## Backups

SQLite is one file — back it up like one:
```bash
sqlite3 /home/deploy/lecturerhub/db.sqlite3 ".backup /home/deploy/backups/db-$(date +%F).sqlite3"
```
Put that in a daily cron job, and back up `media/` (uploaded photos and
documents) alongside it — a simple `rsync`/`tar` to another disk or
off-server storage is enough for a single-user app.

## Troubleshooting

- **502 Bad Gateway** — gunicorn isn't running or the socket path is
  wrong. Check `systemctl status lecturerhub` and `journalctl -u
  lecturerhub`.
- **403 on static files** — check the `deploy` user (or `www-data`, per
  the `Group=` in the systemd unit) can actually read
  `staticfiles/`/`media/`; `chmod -R o+rX` on those two directories if in
  doubt.
- **CSRF failures behind nginx/Apache** — the `X-Forwarded-Proto` header
  set in both the nginx and Apache configs above is required; without it
  Django doesn't know the original request was HTTPS, which breaks CSRF's
  origin check under `config.settings.prod`.
- **`nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in
  use)`** — something else already owns port 80. Check with
  `sudo ss -tlnp | grep :80`. If it's Apache serving other sites, use the
  Apache alternative above rather than stopping Apache; if it's a leftover
  nginx process or an unused Apache install, `sudo systemctl stop apache2
  && sudo systemctl disable apache2` (only if nothing else needs it) or
  `sudo pkill -f nginx` for a stuck nginx process, then retry `systemctl
  start nginx`.
- **"Load cannot follow more than 20 redirections" / infinite HTTPS
  redirect loop** — almost always `SECURE_PROXY_SSL_HEADER` mismatch: the
  proxy in front of Django (Apache, nginx, or a CDN like Cloudflare) isn't
  actually telling Django the request was HTTPS. Diagnose by bypassing
  every layer one at a time:
  1. `curl -skI --resolve yourdomain.com:443:<VPS_IP> https://yourdomain.com/`
     — if this *also* redirects to itself, the bug is on the origin (check
     the `-le-ssl.conf` file's `RequestHeader set X-Forwarded-Proto` value
     — see the certbot section above, this is the most common cause).
  2. If step 1 is fine but the real domain still loops, and it's proxied
     through Cloudflare/another CDN, check that CDN's SSL mode is "Full
     (strict)", not "Flexible".
