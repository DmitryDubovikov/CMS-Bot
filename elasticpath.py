import requests


def get_access_token():
    url = "https://useast.api.elasticpath.com/oauth/access_token"
    payload = {"client_id": "lv9ymiUDkWkV4VpFMvBnO5BjmOCV6IDrUnOJzYxeQ8", "grant_type": "implicit"}

    response = requests.post(url=url, data=payload)
    response.raise_for_status()
    response_data = response.json()

    return response_data


def main():
    access_token = get_access_token()

    print(access_token)


if __name__ == "__main__":
    main()
