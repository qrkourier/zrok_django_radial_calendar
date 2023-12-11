# zrok_django_radial_calendar
Plot events on a radial calendar

## Production

The included `compose.yml` base project file is copied unmodified from [the zrok
docs](https://docs.zrok.io/zrok-public-reserved/compose.yml). All customizations are in `compose.override.yml`.

1. Create an `.env` file in the same directory as `compose.override.yml`.

    ```bash
    # .env
    DJANGO_SECRET_KEY=randomsecret
    ZROK_ENABLE_TOKEN=myzrokaccounttoken
    ```

2. Run the following command to start the server.

    ```bash
    docker compose up --force-recreate --detach --build
    ```

## Development

```bash
pip install -r requirements.txt
DJANGO_SECRET_KEY=$(openssl rand -base64 32) \
    python manage.py runserver
```
