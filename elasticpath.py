import time

import requests

access_token, access_token_expires = None, None


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


def get_image_link_by_id(access_token, image_id):
    url = f"https://useast.api.elasticpath.com/v2/files/{image_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    image_link = response.json()["data"]["link"]["href"]

    return image_link


def add_product_to_customer_cart(access_token, product_id, amount, customer_id):
    url = f"https://useast.api.elasticpath.com/v2/carts/{customer_id}/items"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    payload = {"data": {"id": product_id, "type": "cart_item", "quantity": amount}}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response


def get_customer_cart_items(access_token, customer_id):
    url = f"https://useast.api.elasticpath.com/v2/carts/{customer_id}/items"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()

    return cart_items


def delete_customer_cart_item(access_token, customer_id, item_id):
    url = f"https://useast.api.elasticpath.com/v2/carts/{customer_id}/items/{item_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.delete(url, headers=headers)
    response.raise_for_status()

    return response


def create_customer(access_token, name, email):
    url = "https://useast.api.elasticpath.com/v2/customers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    payload = {
        "data": {
            "type": "customer",
            "name": name,
            "email": email,
            "password": "mysecretpassword",
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response
