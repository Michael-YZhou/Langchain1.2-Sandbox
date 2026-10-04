# LangChain 1.2 Sandbox

A personal sandbox for learning LangChain 1.2 and working with LLM APIs. It's for experiments and notes, not production code.

The material is organized into one directory per chapter. Every file is a standalone script you run directly. There is no package, build step, or test suite.

## Layout

```
.
├── chapter01_summary/
│   └── test.py        # Streams a Qwen "thinking" model response (reasoning, then answer)
├── .env.example       # Template for the required environment variables
└── main.py            # Unused PyCharm template stub
```

## Model provider

LLM calls go to **Alibaba Cloud Model Studio (DashScope / Qwen)** through its OpenAI-compatible endpoint, not to OpenAI. That's why the scripts use the `openai` client with a custom `base_url`.

## Setup

1. Create and activate the conda environment:

   ```bash
   conda create -n langchain1.2 python
   conda activate langchain1.2
   ```

2. Install dependencies. There is no `requirements.txt`, so install what the scripts import:

   ```bash
   pip install openai langchain python-dotenv
   ```

3. Configure credentials:

   ```bash
   cp .env.example .env
   ```

   Then fill in `.env`:

   | Variable             | Purpose                                   |
   | -------------------- | ----------------------------------------- |
   | `LLM_API_KEY`        | Your DashScope / Model Studio API key     |
   | `DASHSCOPE_BASE_URL` | The OpenAI-compatible endpoint URL        |

   `.env` is gitignored. Each script loads it with `load_dotenv()`, and real OS environment variables take precedence over it. Never hardcode keys in scripts.

## Running

```bash
conda activate langchain1.2
python chapter01_summary/test.py
```

Despite its name, `test.py` is a demo, not a pytest test. It sends a prompt to a Qwen thinking model with `enable_thinking` turned on. It prints the streamed reasoning (`reasoning_content`) first, then the final answer (`content`).

## Adding a new chapter

- Create a `chapterNN_<topic>/` directory and put standalone scripts in it.
- Load config with `load_dotenv()` and read values with `os.getenv(...)`.
- If you add a new environment variable, add it to both `.env` and `.env.example`.
