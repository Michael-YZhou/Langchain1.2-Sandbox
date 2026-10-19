from langchain.agents import create_agent
from langchain.agents.middleware import PIIDetectionError, PIIMiddleware
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

try:
    response = agent.invoke(
        {
            "messages": [
                HumanMessage("""
                帮我向 123321ko@gmail.com 发一封邮件
                同时查看银行卡号: 4111-1111-1111-1111
                访问: https://localhost:12345
                确认这是不是 MAC地址: 00-1A-2B-3C-4D-5E
                服务器IP: 192.168.1.1
                """)
            ]
        }
    )
except PIIDetectionError as e:
    # the "block" strategy raises before the model is called, so there is no response to print
    print(f"已拦截: {e}")
    print(f"类型: {e.pii_type}, 匹配: {[m['value'] for m in e.matches]}")
else:
    for msg in response["messages"]:
        msg.pretty_print()