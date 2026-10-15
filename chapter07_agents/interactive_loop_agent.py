from chapter07_agents.agent import SmartAgent


def main():
    agent = SmartAgent()
    print("Chat with Joi. Type 'reset' to clear the history, 'exit' to quit.")

    while True:
        try:
            user_input = input("\nUser: ").strip()
        except (EOFError, KeyboardInterrupt):  # Ctrl-D / Ctrl-C
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("(history cleared)")
            continue

        print("Joi: ", end="")
        agent.chat(user_input)

    print("Bye!")


if __name__ == "__main__":
    main()
