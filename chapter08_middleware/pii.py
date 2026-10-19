from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import HumanMessage

from common.llm import get_chat_model

model = get_chat_model()

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        PIIMiddleware(pii_type="email", strategy="redact", apply_to_input=True),
        PIIMiddleware(pii_type="credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware(pii_type="url", strategy="hash", apply_to_input=True),
        PIIMiddleware(pii_type="mac_address", strategy="mask", apply_to_input=True),
        PIIMiddleware(pii_type="ip", strategy="block", apply_to_input=True),
    ]
)

response = agent.invoke(
    {
        "messages": [
            HumanMessage("""
            帮我向 123321ko@gmail.com 发一封邮件
            同时查看银行卡号: 4111-1111-1111-1111
            访问: https://localhost:12345
            确认这是不是 MAC地址: 00-1A-2B-3C-4D-5E
            """)
        ]
    }
)

for msg in response["messages"]:
    msg.pretty_print()