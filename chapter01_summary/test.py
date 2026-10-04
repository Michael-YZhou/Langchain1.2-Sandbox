from common.llm import get_client_and_model, reasoning_text, thinking_extra_body

client, model = get_client_and_model()

messages = [{"role": "system", "content": ""},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "你好"}]

completion = client.chat.completions.create(
    model=model,  # set DASHSCOPE_MODEL / OLLAMA_MODEL to a deep thinking model
    messages=messages,
    extra_body=thinking_extra_body(),
    stream=True
)
is_answering = False  # Indicates whether the response phase has started
print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
for chunk in completion:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    reasoning = reasoning_text(delta)
    if reasoning is not None:
        if not is_answering:
            print(reasoning, end="", flush=True)
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Full response" + "=" * 20)
            is_answering = True
        print(delta.content, end="", flush=True)
