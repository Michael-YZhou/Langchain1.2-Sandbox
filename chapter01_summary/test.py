from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from the repo root; real OS env vars take precedence

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

messages = [{"role": "user", "content": "你好"}]
completion = client.chat.completions.create(
    model="qwen3.8-max",  # You can replace this with another deep thinking models
    messages=messages,
    extra_body={"enable_thinking": True},
    stream=True
)
is_answering = False  # Indicates whether the response phase has started
print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
for chunk in completion:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Full response" + "=" * 20)
            is_answering = True
        print(delta.content, end="", flush=True)