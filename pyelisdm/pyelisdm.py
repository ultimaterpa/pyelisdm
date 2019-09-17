from urllib.parse import urljoin
from typing import Union

import requests


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
        return Queue(self.session, queue_id)


class Queue:
    def __init__(self, session, queue_id):
        self.session = session
        self.queue_id = queue_id
        self.refresh()

    def refresh(self):
        response = self.session.get(f"v1/queues/{self.queue_id}")
        response.raise_for_status()
        self.json = response.json()

    def upload(self, invoice, values=None):
        files = {"content": open(invoice, "rb")}
        response = self.session.post(f"v1/queues/{self.queue_id}/upload", files=files, data=values)
        response.raise_for_status()
        return Annotation(self.session, response.json()["annotation"].split("/")[-1])

    def export(self, format="json", filter=None):
        params = {"format": format}
        if filter is not None:
            params.update(filter)
        response = self.session.get(f"v1/queues/{self.queue_id}/export", params=params)
        response.raise_for_status()
        return response.json()

    def update(self, payload):
        repsonse = self.session.patch(f"v1/queues/{self.queue_id}", json=payload)
        repsonse.raise_for_status()
        self.refresh()

    @property
    def name(self):
        return self.json["name"]

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Value must have type str!")
        self.update({"name": value})

    @property
    def automation_enabled(self):
        return self.json["automation_enabled"]

    @automation_enabled.setter
    def automation_enabled(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Value must have type bool!")
        self.update({"automation_enabled": value})

    @property
    def automation_level(self):
        return self.json["automation_level"]

    @automation_level.setter
    def automation_level(self, value):
        automation_levels = ("always", "confident", "never")
        if value not in automation_levels:
            raise ValueError(f"Value must be from: {automation_levels}!")
        self.update({"automation_level": value})

    @property
    def default_score_threshold(self):
        return self.json["default_score_threshold"]
    
    @default_score_threshold.setter
    def default_score_threshold(self, value: Union[float, int]):
        if not isinstance(value, (float, int)):
            raise TypeError("Value must have type float or int!")
        if 0 >= value <= 1:
            raise ValueError("Value must be number from interval [0,1]!")
        self.update({"default_score_threshold": value})


class Annotation:
    def __init__(self, session, annotation_id):
        self.session = session
        self.annotation_id = annotation_id
        self.refresh()

    def refresh(self):
        response = self.session.get(f"v1/annotations/{self.annotation_id}")
        response.raise_for_status()
        self.json = response.json()
        self.status = self.json["status"]

    def start(self):
        response = self.session.get(f"v1/annotations/{self.annotation_id}/start")
        response.raise_for_status()
        return response.json()

    def confirm(self):
        response = self.session.post(f"v1/annotations/{self.annotation_id}/confirm")
        response.raise_for_status()
        self.refresh()

    def content(self):
        response = self.session.get(f"v1/annotations/{self.annotation_id}/content")
        response.raise_for_status()
        return response.json()


class URLBaseSession(requests.Session):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)
