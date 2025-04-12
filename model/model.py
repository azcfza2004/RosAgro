import requests
import pprint

api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImMzNWMyODBhLWUyYTYtNDdjOS1hNDI3LTgyODVkMTI3ZDIxYiIsImV4cCI6NDg5Nzk3NDk5Mn0.ZdllhvoIWoaZNAFTOVnf8CqC2-PRjo0QFvFGViGlScNUN4lN5w5uhBG0gDYYGQK3v6vm4QLXs_gbNoTJFGJOYg"
url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

message = "Сколько будет 2 + 2"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-ai/DeepSeek-R1",
    "messages": [
        {
            "role": "system",
            "content": "Agronomist assistant"
        },
        {
            "role": "user",
            "content": message
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    data = response.json()

    #сырые данные
    pprint.pprint(data)

else:
    print(f"\nОшибка! Статус-код: {response.status_code}")
    print("Ответ сервера:", response.text)

print("\nHELLO")

print("HELLO")