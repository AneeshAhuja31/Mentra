import json
import requests
url = "https://7c12-35-240-200-50.ngrok-free.app/api/generate"
headers = {
    "Content-Type": "application/json"
}

data = {
    "model": "gemma3:4b",
    "prompt": "how are you",
    "stream": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
  print("Response:", response.json())
else:
  print(f"Request failed with status code {response.status_code}")
