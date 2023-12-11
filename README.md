# zrok_django_radial_calendar
Web app that plot events on a radial calendar.

![events](https://github.com/qrkourier/zrok_django_radial_calendar/assets/1434400/26ab2463-daa3-409c-9cc7-c309f5e70d27)


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
