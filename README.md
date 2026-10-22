# LangChain 1.2 Sandbox

A personal sandbox for learning LangChain 1.2 and working with LLM APIs. It's for experiments and notes, not production code.

The material is organized into one directory per chapter. Every file is a standalone script you run directly. There is no package, build step, or test suite.

## Layout

```
.
├── common/
│   └── llm.py         # Builds the chat model for the provider chosen by LLM_PROVIDER
├── chapter01_summary/
│   └── openai_sdk.py  # Raw OpenAI-SDK DashScope streaming example
├── chapter02_models/
│   └── init_chat_model.py  # Streams a Qwen "thinking" model response (reasoning, then answer)
├── chapter03_langsmith/
│   ├── chat_openai.py      # Streams Qwen through ChatOpenAI (answer only, no reasoning)
│   └── init_chat_model.py  # Copy of chapter02_models/init_chat_model.py, for LangSmith tracing
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
│   ├── model_fall_back.py       # ModelFallbackMiddleware: retry a failed call with another model
│   ├── to_do_list.py            # TodoListMiddleware: plan a multi-step task with write_todos
│   ├── tool_retry.py            # ToolRetryMiddleware: retry a tool call that raises an error
│   ├── model_retry.py           # ModelRetryMiddleware: retry a failed model call, then reply with the error
│   └── filesystem_file_search.py  # FilesystemFileSearchMiddleware: glob and grep tools over the repo
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
python -m chapter02_models.init_chat_model                      # uses LLM_PROVIDER from .env
LLM_PROVIDER=ollama python -m chapter02_models.init_chat_model  # one-off switch to local Ollama
```

`python chapter02_models/init_chat_model.py` fails with `ModuleNotFoundError: No module named 'common'`. PyCharm run configurations work as-is, because they add the project root to `PYTHONPATH`.

`chapter02_models/init_chat_model.py` sends a prompt to a thinking model with thinking turned on. It prints the streamed reasoning first, then the final answer.

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

`chapter08_middleware/to_do_list.py` adds `TodoListMiddleware`, which gives the agent a `write_todos` tool and keeps the current list in `state["todos"]`. The agent also has three tools: `get_weather`, `check_stock` and `multiply` (fake results). The task has three steps, and the last one depends on the second: check the weather in Beijing, check the laptop stock, then multiply the stock by 3. The middleware's built-in prompt tells the model to skip the list for simple requests, so the system prompt tells it to write the list first and mark each item `completed` as soon as it's done. The script prints every message, where you can see each `write_todos` call, then the final list from `response["todos"]`. In a test run the agent called `write_todos` three times. First it wrote the list and ran `get_weather` and `check_stock` in the same turn. Then it marked those two `completed` and called `multiply(52, 3)`. Finally it marked the last item `completed` and answered 156. It updates the list once per turn, not after every tool call, and it had two items `in_progress` at once: the middleware's prompt asks for one at a time but doesn't enforce it.

`chapter08_middleware/tool_retry.py` adds `ToolRetryMiddleware` to an agent with a fake `check_weather` tool. The tool raises `TimeoutError` on its first two calls and succeeds on the third, printing a line on each call. The middleware retries only on `TimeoutError` (`retry_on=(TimeoutError,)`), up to 3 times after the first call, with exponential backoff (0.5s, then 1s, capped at `max_delay=10`, plus ±25% jitter). The retries happen inside one tool call, so the conversation shows a single tool call and a single `ToolMessage` with the weather; the model never sees the failures. With `on_failure="continue"`, if every retry fails the error goes back to the model as a `ToolMessage` instead of stopping the run. Lower `max_retries` to 1 to see that.

`chapter08_middleware/model_retry.py` adds `ModelRetryMiddleware`. Like the fallback demo, it copies the default model with a name that doesn't exist, so every call fails with `NotFoundError` (404). `retry_on` is a function, not a tuple of exception types: the middleware calls it after each failed call and retries only if it returns `True`. Here it prints the failure and always returns `True`, so the output shows three failures (the first call plus `max_retries=2`), 0.5s and then 1s apart. With `on_failure="continue"`, the last error comes back as an `AIMessage` ("Model call failed after 3 attempts with NotFoundError: ...") and the run ends normally; `"error"` would raise it instead. Unlike `ModelFallbackMiddleware`, retry calls the same model again, so it helps with short-lived errors such as timeouts or rate limits, not a bad model name. As with the fallback demo, the fake name only works on DashScope: with `LLM_PROVIDER=ollama` the call succeeds and nothing is retried.

`chapter08_middleware/filesystem_file_search.py` adds `FilesystemFileSearchMiddleware`, which gives the agent two tools: `glob_search` (find files by name pattern) and `grep_search` (search file contents with a regex), so the agent passes `tools=[]`. Both are limited to `root_path`, and they show paths relative to it with a leading `/`. The script builds `root_path` from `__file__` (the repo root), because a relative path like `"../"` is resolved against the directory you run from, not the script's folder. `use_ripgrep=False` uses the pure-Python search, and `max_file_size_mb` skips larger files. The agent is asked which Python files define `multiply`. It found `chapter07_agents/agent.py`, `human_in_the_loop.py` and `to_do_list.py`.

## Adding a new chapter

- Create a `chapterNN_<topic>/` directory and put standalone scripts in it.
- Get a chat model with `from common.llm import get_chat_model` instead of building one yourself.
- If you add a new environment variable, add it to both `.env` and `.env.example`.
