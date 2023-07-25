# CMS-Bot


В корневой папке расположить файл .env c данными:
```
TELEGRAM_TOKEN=changeme
```

Активировать виртуальное окружение:
```
poetry shell
```

Установить зависимости:
```
make install
```

Запустить базу REDIS:
```
docker run -d --name redis_db -p 6379:6379 redis
```

Запустить бота:
```
poetry run python tg_bot.py
```