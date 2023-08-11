# CMS-Bot

Telegram bot with API based integration with Elastic Path (https://www.elasticpath.com/) online store.

Bot allowes customers to:

* get list of produsts with detailed information
* add (remove) products to cart, view cart 
* provide email to manager to complete purchase

![image](https://github.com/DmitryDubovikov/CMS-Bot/blob/main/cart.png)

## How to run

Create an .env file in the project directory:
```
TELEGRAM_TOKEN=changeme
ELASTICPATH_CLIENT_ID=changeme
ELASTICPATH_CLIENT_SECRET=changeme
```

Activate virtual environment:
```
poetry shell
```

Install dependencies:
```
make install
```
for Windows:
```
poetry install
```

Run REDIS database:
```
docker run -d --name redis_db -p 6379:6379 redis
```

Run bot:
```
make run 
```
for Windows:
```
poetry run python cms_bot.py
```
