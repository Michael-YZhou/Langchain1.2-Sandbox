"""SummarizationMiddleware: compress old chat history with a small model before the agent replies.

The agent chats with the default model; a cheap DashScope flash model writes the summary.
The triggers are tiny on purpose so a short history is enough to fire it.
"""
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

from common.llm import get_chat_model, get_summary_model

# "fraction" triggers read max_input_tokens from the summary model's profile,
# so set it explicitly: 0.001 * 128000 = 128 tokens
summary_model = get_summary_model(profile={"max_input_tokens": 128000})

agent = create_agent(
    model=get_chat_model(thinking=False),
    system_prompt="你是Joi，一个友好的智能助手。",
    middleware=[
        SummarizationMiddleware(
            model=summary_model,
            # summarise when ANY condition is met
            trigger=[("messages", 6), ("tokens", 100), ("fraction", 0.001)],
            # keep counts messages from the end of the input, the new question included:
            # 3 = the last history turn (user + ai) + the new question; everything before is summarised
            keep=("messages", 3),
            # replaces the built-in English prompt so the summary comes back in Chinese;
            # the middleware fills {messages} with the messages being summarised
            summary_prompt="对历史消息的摘要，消息列表如下\n{messages}"
        )
    ],
)

# 6 messages of earlier conversation
history = [
    {"role": "user", "content": "你好，我叫小周，是一名Python后端工程师。"},
    {"role": "assistant", "content": "你好小周！很高兴认识你，有什么可以帮你的？"},
    {"role": "user", "content": "我在学LangChain 1.2，下周要在公司做一次分享。"},
    {"role": "assistant", "content": "好的！分享可以从模型、提示词模板、工具调用和Agent几个部分展开。"},
    {"role": "user", "content": "我最喜欢的编程语言是Python，平时喜欢喝美式咖啡。"},
    {"role": "assistant", "content": "记住了：你喜欢Python和美式咖啡。"},
]


def main():
    question = "你还记得我叫什么、在准备什么、喜欢喝什么吗？"
    result = agent.invoke({"messages": [*history, {"role": "user", "content": question}]})

    # the state now holds: summary message + the kept recent messages + the new AI reply
    print(f"Messages in: {len(history) + 1}, messages after summarisation: {len(result['messages'])}\n")
    for message in result["messages"]:
        print(f"[{message.type}] {message.content}\n")


if __name__ == "__main__":
    main()
