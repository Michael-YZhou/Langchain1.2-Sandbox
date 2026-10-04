# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal learning workspace for LangChain 1.2 and LLM APIs, organized into one directory per chapter (`chapter01_summary/`, ...). There is no package, build system, test suite, linter config, or dependency manifest. Each file is a standalone script meant to be run directly.

`main.py` at the root is the unused PyCharm template stub.

## Environment

- Python interpreter: the conda env `langchain1.2` (`~/miniconda3/envs/langchain1.2`), as configured in `.idea/misc.xml`. Activate it with `conda activate langchain1.2` before running anything.
- No `requirements.txt` exists. Install packages straight into that env (e.g. `pip install openai langchain python-dotenv`).
- LLM calls go to Alibaba Cloud Model Studio (DashScope / Qwen) through its OpenAI-compatible endpoint, not to OpenAI.
- Config comes from env vars, loaded in each script with `load_dotenv()` from a gitignored `.env` at the repo root (see `.env.example` for the keys: `LLM_API_KEY` for the API key, `DASHSCOPE_BASE_URL` for the endpoint). Real OS env vars take precedence over `.env`. Never hardcode keys in scripts; when adding a new variable, add it to both `.env` and `.env.example`.

## Running

```bash
conda activate langchain1.2
python chapter01_summary/test.py
```

Despite its name, `test.py` is a demo script, not a pytest test. It streams a Qwen "thinking" model response (`extra_body={"enable_thinking": True}`), printing `delta.reasoning_content` first and then `delta.content`.
