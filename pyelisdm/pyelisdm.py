import requests
from urllib.parse import urljoin


URL = "https://api.elis.rossum.ai"
CONTENT_TYPE = {"Content-Type": "application/json"}


class Elis:
    def __init__(self, username, password, base_url=URL, max_token_lifetime_s=None):
        self.username = username
        self.password = password
        self.max_token_lifetime_s = max_token_lifetime_s
        self.session = URLBaseSession(base_url=base_url)

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self):
        response = self.session.post(
            "v1/auth/login",
            headers=CONTENT_TYPE,
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        self.session.headers.update({"Authorization": f"token {response.json()['key']}"})

    def logout(self):
        response = self.session.post("v1/auth/logout")
        response.raise_for_status()

    def queues(self, ordering=None):
        response = self.session.get("v1/queues", params={"ordering": ordering})
        response.raise_for_status()
        return response.json()

    def queue(self, queue_id):
        response = self.session.get(f"v1/queues/{queue_id}")
        response.raise_for_status()
        return Queue(self.session, response.json())


class Queue:
    def __init__(self, session, response):
        self.session = session
        self.id = response["id"]
        self.url = response["url"]

    def upload(self, invoice, values=None):
        files = {"content": open(invoice, "rb")}
        response = self.session.post(f"v1/queues/{self.id}/upload", files=files, data=values)
        response.raise_for_status()

    def export(self, format="json", filter=None):
        params = {"format": format}
        if filter is not None:
            params.update(filter)
        response = self.session.get(f"v1/queues/{self.id}/export", params=params)
        response.raise_for_status()
        return response.json()
        


class Schema:
    pass


class URLBaseSession(requests.Session):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)
