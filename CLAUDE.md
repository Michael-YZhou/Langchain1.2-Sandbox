# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal learning workspace for LangChain 1.2 and LLM APIs, organized into one directory per chapter (`chapter01_summary/`, ...). There is no package, build system, test suite, linter config, or dependency manifest. Each file is a standalone script meant to be run directly.

`main.py` at the root is the unused PyCharm template stub.

## Environment

- Python interpreter: the conda env `langchain1.2` (`~/miniconda3/envs/langchain1.2`), as configured in `.idea/misc.xml`. Activate it with `conda activate langchain1.2` before running anything.
- No `requirements.txt` exists. Install packages straight into that env (e.g. `pip install openai langchain python-dotenv`).
- LLM calls go through LangChain chat models (`init_chat_model`) to one of two backends, chosen by `LLM_PROVIDER`: `dashscope` (Alibaba Cloud Model Studio / Qwen, the default) or `ollama` (local server). Not to OpenAI.
- `common/llm.py` owns provider selection. Scripts call `get_chat_model(thinking=True)` and `reasoning_text(chunk)` instead of building models or reading provider env vars themselves. DashScope uses `ChatDeepSeek` pointed at its OpenAI-compatible endpoint (plain `ChatOpenAI` drops `reasoning_content`) with `extra_body={"enable_thinking": ...}`; Ollama uses `ChatOllama` with `reasoning=...` against the native API, so `OLLAMA_BASE_URL` has no `/v1`. Both put streamed thinking text in `chunk.additional_kwargs["reasoning_content"]`.
- Config comes from env vars, loaded by `common/llm.py` with `load_dotenv()` from a gitignored `.env` at the repo root (keys in `.env.example`: `LLM_PROVIDER`, `DASHSCOPE_API_KEY`/`DASHSCOPE_BASE_URL`/`DASHSCOPE_MODEL`, `OLLAMA_BASE_URL`/`OLLAMA_MODEL`). Real OS env vars take precedence over `.env`. Never hardcode keys in scripts; when adding a new variable, add it to both `.env` and `.env.example`.

## Running

Run scripts as modules from the repo root so `common` is importable (`python chapter01_summary/test.py` fails with `ModuleNotFoundError`):

```bash
conda activate langchain1.2
python -m chapter01_summary.test
LLM_PROVIDER=ollama python -m chapter01_summary.test
```

Despite its name, `test.py` is a demo script, not a pytest test. It streams a thinking model's response with `model.stream()`, printing the reasoning first and then `chunk.content`. `test_0.py` is the raw OpenAI-SDK DashScope example, kept for comparison.
