import requests
from urllib.parse import urljoin


URL = "https://api.elis.rossum.ai"
CONTENT_TYPE = {"Content-Type": "application/json"}


class Elis:
    def __init__(self, username, password, base_url=URL, max_token_lifetime_s=None):
        self.username = username
        self.password = password
        self.max_token_lifetime_s = max_token_lifetime_s
        self._session = URLBaseSession(base_url=base_url)

    def __enter__(self):
        self._login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logout()

    def _login(self):
        response = self._session.post(
            "v1/auth/login",
            headers=CONTENT_TYPE,
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        self._session.headers.update({"Authorization": f"token {response.json()['key']}"})

    def _logout(self):
        response = self._session.post("v1/auth/logout")
        response.raise_for_status()

    def queues(self, ordering=None):
        response = self._session.get("v1/queues", params={"ordering": ordering})
        response.raise_for_status()
        return response.json()

    def queue(self, queue_id):
        response = self._session.get(f"v1/queues/{queue_id}")
        response.raise_for_status()
        return Queue(response.json())


class Queue:
    def __init__(self, response):
        self.id = response["id"]
        self.url = response["url"]

    def upload(self):
        pass

    def export(self):
        pass


class Schema:
    pass


class URLBaseSession(requests.Session):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)
