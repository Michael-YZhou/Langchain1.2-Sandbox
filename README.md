# LangChain 1.2 Sandbox

A personal sandbox for learning LangChain 1.2 and working with LLM APIs. It's for experiments and notes, not production code.

The material is organized into one directory per chapter. Every file is a standalone script you run directly. There is no package, build step, or test suite.

## Layout

```
.
├── common/
│   └── llm.py         # Builds the chat model for the provider chosen by LLM_PROVIDER
├── chapter01_summary/
│   └── test_0.py      # Raw OpenAI-SDK DashScope streaming example
├── chapter02_models/
│   └── test.py        # Streams a Qwen "thinking" model response (reasoning, then answer)
├── chapter03_langsmith/
│   ├── chat_openai.py      # Streams Qwen through ChatOpenAI (answer only, no reasoning)
│   └── init_chat_model.py  # Copy of chapter02_models/test.py, for LangSmith tracing
├── chapter04_prompt_template/
│   └── chat_prompt_template.py  # Builds the prompt with ChatPromptTemplate, then streams it
├── chapter05_tools/
│   └── chat_prompt_template.py  # Tool calling: model requests get_weather, gets the result, answers
├── chapter06_structured_output/
│   └── structured_output.py     # with_structured_output: raw reply plus a parsed Pydantic MovieModel
├── chapter07_agents/
│   ├── agent.py                 # create_agent with three tools and chat history kept across turns
│   └── interactive_loop_agent.py  # Chat with that agent in the terminal (reset / exit)
├── chapter08_middleware/
│   ├── summarization.py         # SummarizationMiddleware: a small model summarises old history
│   ├── human_in_the_loop.py     # HumanInTheLoopMiddleware: approve or reject each tool call
│   ├── pii.py                   # PIIMiddleware: redact, mask, hash or block PII in the input
│   └── model_fall_back.py       # ModelFallbackMiddleware: retry a failed call with another model
├── .env.example       # Template for the required environment variables
├── requirements.txt   # Pinned dependencies for the whole course
└── main.py            # Unused PyCharm template stub
```

## Model providers

Scripts can talk to either of two backends, chosen by `LLM_PROVIDER`:

- `dashscope`: **Alibaba Cloud Model Studio (DashScope / Qwen)** in the cloud
- `ollama`: a local **Ollama** server

The scripts use LangChain chat models built with `init_chat_model`. `common/llm.py` reads the provider's settings and returns a ready model with thinking turned on. DashScope goes through `ChatDeepSeek` pointed at its OpenAI-compatible endpoint, because plain `ChatOpenAI` drops the reasoning text. Ollama goes through `ChatOllama` and its native API. Both put the streamed reasoning in `chunk.additional_kwargs["reasoning_content"]`.

## Setup

1. Create and activate the conda environment:

   ```bash
   conda create -n langchain1.2 python
   conda activate langchain1.2
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   It pins the whole course stack, not just what the current scripts import. The RAG / document-parsing block at the bottom stays commented out until those chapters.

3. Configure credentials:

   ```bash
   cp .env.example .env
   ```

   Then fill in `.env`:

   | Variable             | Purpose                                       |
   | -------------------- | --------------------------------------------- |
   | `LLM_PROVIDER`       | `dashscope` (default) or `ollama`             |
   | `DASHSCOPE_API_KEY`  | Your DashScope / Model Studio API key         |
   | `DASHSCOPE_BASE_URL` | DashScope's OpenAI-compatible endpoint URL    |
   | `DASHSCOPE_MODEL`    | Cloud model name, e.g. `qwen3.8-max`          |
   | `DASHSCOPE_SUMMARY_MODEL` | Small model for summarising, e.g. `qwen-flash` (chapter08) |
   | `OLLAMA_BASE_URL`    | Usually `http://localhost:11434` (no `/v1`)   |
   | `OLLAMA_MODEL`       | A model you've pulled (see `ollama list`)     |
   | `LANGSMITH_*`        | LangSmith tracing settings, for chapter03     |

   `.env` is gitignored. `common/llm.py` loads it with `load_dotenv()`, and real OS environment variables take precedence over it. Never hardcode keys in scripts.

## Running

Run scripts as modules from the repo root, so that `common` can be imported:

```bash
conda activate langchain1.2
python -m chapter02_models.test                      # uses LLM_PROVIDER from .env
LLM_PROVIDER=ollama python -m chapter02_models.test  # one-off switch to local Ollama
```

`python chapter02_models/test.py` fails with `ModuleNotFoundError: No module named 'common'`. PyCharm run configurations work as-is, because they add the project root to `PYTHONPATH`.

Despite its name, `chapter02_models/test.py` is a demo, not a pytest test. It sends a prompt to a thinking model with thinking turned on. It prints the streamed reasoning first, then the final answer.

`chapter05_tools/chat_prompt_template.py` shows a full tool-calling round trip. It binds a `get_weather` tool to the model, runs the tool call the model asks for, and sends the result back so the model can give a final answer. The conversation history is built from `prompt_value.to_messages()`. The raw `messages` list passed to `ChatPromptTemplate` still has its `{placeholders}`, so the model would see those literally if you sent it that list.

`chapter06_structured_output/structured_output.py` asks for structured output. `with_structured_output(MovieModel, include_raw=True)` makes `invoke()` return a dict instead of text: `raw` is the model's original `AIMessage`, `parsed` is the validated `MovieModel` (title, year, director, rating), and `parsing_error` holds the exception if parsing failed (otherwise `None`). The dict is pretty-printed with `rich`. Without `include_raw`, `invoke()` returns just the `MovieModel`. The messages are a plain list, not a `ChatPromptTemplate`, so the `{name}` in the system message is sent as-is.

`chapter07_agents/agent.py` builds an agent with `create_agent` and three tools (`get_weather`, `check_stock`, `multiply`). `SmartAgent` keeps the whole conversation, including tool calls, in `self.messages`, so a follow-up like "multiply the last result by 2" works. `reset()` clears it. `python -m chapter07_agents.interactive_loop_agent` lets you chat with the same agent in the terminal. Type `reset` to clear the history and `exit` to quit.

`chapter08_middleware/summarization.py` adds `SummarizationMiddleware` to an agent. The default model chats, while a small DashScope model from `get_summary_model()` (`DASHSCOPE_SUMMARY_MODEL`, thinking off) writes the summary with a Chinese `summary_prompt`. The triggers are tiny on purpose, so a 6-message history fires them: 6 messages, 100 tokens, or 0.001 of `max_input_tokens`. The `fraction` trigger reads `max_input_tokens` from the summary model's profile, so the script sets `profile={"max_input_tokens": 128000}`. `keep=("messages", 3)` counts from the end of the input, the new question included. It keeps the last history turn plus the new question and replaces everything before them with one summary message.

`chapter08_middleware/human_in_the_loop.py` adds `HumanInTheLoopMiddleware` to the chapter07 agent. Before any tool runs, the agent pauses and shows the tool name, its arguments and a description. Type `approve` (or press Enter) to run it, or `reject` with an optional reason, which goes back to the model instead of the tool result. `check_stock` is configured with `InterruptOnConfig` to allow only approve and reject. To resume after a pause, the agent needs to remember where it stopped, so it has an `InMemorySaver` checkpointer and each `invoke` passes a `thread_id` in its config. The checkpointer keeps the conversation for that thread, so `chat()` sends only the new message, and `reset()` just starts a new thread. `main()` asks four questions, prints the saved history (tool calls, results and rejections included), then resets and checks the earlier result is forgotten. The script reads your decisions from the terminal, so pipe them in to run it unattended:

```bash
printf 'approve\nreject\n库存系统正在维护\napprove\napprove\n' | python -m chapter08_middleware.human_in_the_loop
```

`chapter08_middleware/pii.py` adds five `PIIMiddleware` rules with `apply_to_input=True`, so personal data in the user message is replaced before the model sees it. Each rule uses a different strategy: emails become `[REDACTED_EMAIL]` (`redact`), the card number becomes `****-****-****-1111` (`mask`), the URL becomes `<url_hash:...>` (`hash`), and the MAC address keeps only its last group (`mask`). The script prints the whole conversation, so you can see the rewritten human message. The built-in detectors are strict: a card number must pass the Luhn checksum and a MAC address needs exactly 6 groups, or they go through unchanged, which is why the inputs use the test card `4111-1111-1111-1111`. The `ip` rule uses `block`, which raises `PIIDetectionError` instead of rewriting. The input contains `192.168.1.1`, so the run stops before the model is called, and the script catches the error and prints the blocked type and value (`e.pii_type`, `e.matches`). Remove the IP line to see the other rules rewrite the message and the model reply.

`chapter08_middleware/model_fall_back.py` adds `ModelFallbackMiddleware` with the summary model as the fallback. When the primary model raises an error, the middleware retries the same request with each fallback model in order and re-raises the last error if they all fail. To force a failure, the script copies the default model with a model name that doesn't exist (`model_copy(update={"model_name": "no-such-model"})`), so the API rejects the call. It prints `response_metadata["model_name"]` of the reply, which shows the fallback (`qwen-flash`) answered. The middleware swallows the primary's error without logging it. The fake name only works on DashScope: `ChatOllama` calls the field `model`, so with `LLM_PROVIDER=ollama` the primary succeeds and the fallback never runs.

## Adding a new chapter

- Create a `chapterNN_<topic>/` directory and put standalone scripts in it.
- Get a chat model with `from common.llm import get_chat_model` instead of building one yourself.
- If you add a new environment variable, add it to both `.env` and `.env.example`.
