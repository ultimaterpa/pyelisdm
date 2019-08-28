import requests

URL = "https://api.elis.rossum.ai/v1"
CONTENT_TYPE = {"Content-Type": "application/json"}


class Elis:
    def __init__(self, username, password, url=URL, max_token_lifetime_s=None):
        self.username = username
        self.password = password
        self.url = url
        self.max_token_lifetime_s = max_token_lifetime_s
        self._session = requests.Session()
        self._authorization = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._authorization:
            self.logout()

    def login(self):
        response = self._session.post(
            f"{URL}/auth/login",
            headers=CONTENT_TYPE,
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        self._session.headers.update({"Authorization": f"token {response.json()['key']}"})

    def logout(self):
        response = self._session.post(f"{URL}/auth/logout")
        response.raise_for_status()

    def queues(self, ordering=None):
        response = self._session.get(f"{URL}/queues", params={"ordering": ordering})
        response.raise_for_status()
        return response.json()

    def queue(self, queue_id):
        response = self._session.get(f"{URL}/queues/{queue_id}")
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
