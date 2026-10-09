from langchain_core.prompts import ChatPromptTemplate

from common.llm import get_chat_model, reasoning_text

model = get_chat_model()  # set DASHSCOPE_MODEL / OLLAMA_MODEL to a deep thinking model

messages = [
    ("system", "你是一个友好的AI助手，你的名字叫{name}"),
    ("user", "你好，你最近怎么样？"),
    ("assistant", "我很好，谢谢"),
    ("user", "{user_input}"),
]

# provide prompt template
chat_prompt_template = ChatPromptTemplate.from_messages(messages)

# provide value to prompt template
prompt_value = chat_prompt_template.invoke({"name":"Joi", "user_input":"2 + 2 = ?"})

# call LLM with constructed prompt
is_answering = False  # Indicates whether the response phase has started
print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
for chunk in model.stream(prompt_value):
    reasoning = reasoning_text(chunk)
    if reasoning and not is_answering:
        print(reasoning, end="", flush=True)
    if chunk.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Full response" + "=" * 20)
            is_answering = True
        print(chunk.content, end="", flush=True)
print()
