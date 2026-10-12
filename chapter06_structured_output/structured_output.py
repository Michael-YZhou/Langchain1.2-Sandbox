from pydantic import BaseModel, Field
from common.llm import get_chat_model
from rich import print as rprint

class MovieModel(BaseModel):
    """电影信息"""
    title: str = Field(description="电影标题")
    year: int = Field(description="上映年份")
    director: str = Field(description="导演")
    rating: float = Field(description="评分（10分制）")

model = get_chat_model()  # set DASHSCOPE_MODEL / OLLAMA_MODEL to a deep thinking model
structured_model = model.with_structured_output(MovieModel, include_raw=True)

messages = [
    ("system", "你是一个友好的AI助手，你的名字叫{name}"),
    ("user", "你好，你最近怎么样？"),
    ("assistant", "我很好，谢谢"),
    ("user", "给我介绍一下星际穿越这部电影"),
]

# invoke model
response = structured_model.invoke(messages)

rprint(response)
