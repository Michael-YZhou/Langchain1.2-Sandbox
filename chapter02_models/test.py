from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from common.llm import get_chat_model, reasoning_text

model = get_chat_model()  # set DASHSCOPE_MODEL / OLLAMA_MODEL to a deep thinking model

messages = [
    SystemMessage(""),
    HumanMessage(""),
    AIMessage(""),
    HumanMessage("你好"),
]

is_answering = False  # Indicates whether the response phase has started
print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
for chunk in model.stream(messages):
    reasoning = reasoning_text(chunk)
    if reasoning and not is_answering:
        print(reasoning, end="", flush=True)
    if chunk.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Full response" + "=" * 20)
            is_answering = True
        print(chunk.content, end="", flush=True)
print()
