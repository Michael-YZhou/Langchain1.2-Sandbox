import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()  # loads .env from the repo root; real OS env vars take precedence

api_key = os.getenv("DASHSCOPE_API_KEY")
client = ChatOpenAI(
    # If the environment variable is not set, replace it with your Model Studio API key: api_key="sk-xxx"
    api_key=SecretStr(api_key) if api_key else None,
    base_url="https://ws-z81ddjukrv6vbmhf.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
    model="qwen3.8-max",  # You can replace this with another deep thinking models
    extra_body={"enable_thinking": True},
)

# ChatOpenAI drops reasoning_content, so only the answer is streamed
for chunk in client.stream("Who are you"):
    print(chunk.content, end="", flush=True)
print()
