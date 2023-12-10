# zrok_django_radial_calendar
Plot events on a radial calendar

## Production

```bash
# .env
DJANGO_SECRET_KEY=soopersecret
```

```bash
docker compose up --force-recreate --detach --build
```

## Development

```bash
pip install -r requirements.txt
DJANGO_SECRET_KEY=$(openssl rand -base64 32) \
    python manage.py runserver
```
