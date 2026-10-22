from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.messages import HumanMessage

from common.llm import get_chat_model, get_summary_model

# a model name the API doesn't know, so the primary call fails and the fallback takes over
model = get_chat_model().model_copy(update={"model_name": "no-such-model"})
fallback_model = get_summary_model()

agent = create_agent(
    model=model,
    middleware=[
        ModelFallbackMiddleware(
            fallback_model
        )
    ]
)

response = agent.invoke({"messages": [HumanMessage("用一句话介绍你自己")]})

answer = response["messages"][-1]
print(f"回答模型: {answer.response_metadata.get('model_name')}")
answer.pretty_print()
