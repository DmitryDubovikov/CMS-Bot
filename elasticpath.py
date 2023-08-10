import time

import requests

access_token, access_token_expires = None, None


def get_products(access_token):
    url = "https://useast.api.elasticpath.com/pcm/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def get_product_by_id(access_token, product_id):
    url = f"https://useast.api.elasticpath.com/pcm/products/{product_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["data"]


def get_client_credentials_token(client_id, client_secret):
    global access_token, access_token_expires

    url = "https://useast.api.elasticpath.com/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    if access_token is None or access_token_expires <= int(time.time()):
        response = requests.post(url=url, data=payload)
        response.raise_for_status()
        response_data = response.json()

        access_token = response_data["access_token"]
        access_token_expires = response_data["expires"]

        return response_data["access_token"]

    return access_token


def main():
    # access_token = get_client_credentials_token()
    # print(access_token)

    # products = get_products(access_token)
    # # print(products)

    # customer_id = "fa7e3cf3-e852-4864-9896-e9b4332a08c7"
    pass


if __name__ == "__main__":
    main()
