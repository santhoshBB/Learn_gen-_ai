import requests

class RemoteEmbedding:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> list[float]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"model": self.model, "input": text}
        response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=data)
        return response.json()["data"][0]["embedding"]

class LocalEmbedding:
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    def embed(self, text: str) -> list[float]:
        data = {"model": self.model, "input": text}
        response = requests.post(f"{self.url}/embed", json=data)
        return response.json()["embedding"]
