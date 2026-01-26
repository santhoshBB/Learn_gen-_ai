# import requests
from openai import OpenAI

# class RemoteLLM:
#     def __init__(self, api_key: str, base_url: str, model: str):
#         self.api_key = api_key
#         self.base_url = base_url
#         self.model = model

#     def generate(self, prompt: str) -> str:
#         headers = {"Authorization": f"Bearer {self.api_key}"}
#         data = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
#         response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
#         return response.json()["choices"][0]["message"]["content"]

# class LocalLLM:
#     def __init__(self, url: str, model: str):
#         self.url = url
#         self.model = model

#     def generate(self, prompt: str) -> str:
#         data = {"model": self.model, "prompt": prompt}
#         response = requests.post(f"{self.url}/generate", json=data)
#         return response.json()["response"]

class LocalLLM:
    def __init__(self, base_url: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key="none")
        self.model = model

    def create(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )


class RemoteLLM:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def create(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )

