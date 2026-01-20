import requests
# from langchain_community.embeddings import OllamaEmbeddings

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

# class LocalEmbedding:
#     def __init__(self, url: str, model: str):
#         self.model = model
#         self.client = OllamaEmbeddings(
#             model=model,
#         )

#     def embed(self, text: str) -> list[float]:
#         return self.client.embed_query(text)
