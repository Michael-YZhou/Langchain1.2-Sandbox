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

## Adding a new chapter

- Create a `chapterNN_<topic>/` directory and put standalone scripts in it.
- Get a chat model with `from common.llm import get_chat_model` instead of building one yourself.
- If you add a new environment variable, add it to both `.env` and `.env.example`.
