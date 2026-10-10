from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from common.llm import get_chat_model, reasoning_text
from rich import print as rprint

# create tool args schema
class WhetherSchema(BaseModel):
    city: str = Field(default="北京", description="具体城市名称")

# create tool function
@tool(description="获取城市的天气情况", args_schema=WhetherSchema)
def get_weather(city: str):
    return f"{city}多云转晴"

model = get_chat_model()  # set DASHSCOPE_MODEL / OLLAMA_MODEL to a deep thinking model

# bind tools to the model
model_with_tools = model.bind_tools([get_weather])

messages = [
    ("system", "你是一个友好的AI助手，你的名字叫{name}"),
    ("user", "你好，你最近怎么样？"),
    ("assistant", "我很好，谢谢"),
    ("user", "{user_input}"),
]

# provide prompt template
chat_prompt_template = ChatPromptTemplate.from_messages(messages)

# provide value to prompt template
prompt_value = chat_prompt_template.invoke({"name":"Joi", "user_input":"今天杭州的天气怎么样？"})

# the filled-in messages; `messages` above still holds the raw {placeholders}
history = prompt_value.to_messages()

# invoke model, get an Assistant msg, since user asking whether, model will request to call tools
response = model_with_tools.invoke(history)

history.append(response)

# 取出响应中的tool_calls字段信息
tool_calls = response.tool_calls

for tool_call in tool_calls:
    if tool_call["name"] == "get_weather":
        tool_message = get_weather.invoke(tool_call)
        history.append(tool_message)

final_response = model_with_tools.invoke(history)

history.append(final_response)

for message in history:
    rprint(message)


# call LLM with constructed prompt
# is_answering = False  # Indicates whether the response phase has started
# print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
# for chunk in model_with_tools.stream(prompt_value):
#     reasoning = reasoning_text(chunk)
#     if reasoning and not is_answering:
#         print(reasoning, end="", flush=True)
#     if chunk.content:
#         if not is_answering:
#             print("\n" + "=" * 20 + "Full response" + "=" * 20)
#             is_answering = True
#         print(chunk.content, end="", flush=True)
# print()
