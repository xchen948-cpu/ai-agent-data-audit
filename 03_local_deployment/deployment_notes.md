# Local Deployment Log: DB-GPT + Ollama on an 8 GB MacBook Air

Goal: run a fully private data agent (no data leaves the machine, no API key,
zero cost) and compare it with cloud agents on the same tasks.

Stack: DB-GPT 0.8.1 · Ollama · macOS (Apple Silicon, 8 GB RAM)

## Timeline of failures and fixes

### 1. Install script leaves the app layer missing
The official one-line installer registered the `dbgpt` CLI, but
`dbgpt start webserver` failed with `No module named 'dbgpt_app'` — the core
library was installed without the application stack. A whole day was lost
debugging this through a chat assistant that could only see pasted error
messages.

**Fix:** `pip install dbgpt_app` (pulls dbgpt-serve, dbgpt-client, chromadb, etc.).

### 2. `--profile ollama` documented but not implemented
The CLI help lists an `ollama` profile; the code raises
`Unknown profile 'ollama'. Valid profiles: openai, kimi, qwen, minimax, glm, custom, default`.
Docs and code out of sync.

**Fix:** use the `custom` (OpenAI-compatible) profile pointed at Ollama's
OpenAI-compatible endpoint:

```toml
[[models.llms]]
name = "qwen2.5:3b"
provider = "proxy/openai"
api_base = "http://localhost:11434/v1"
api_key = "ollama"          # placeholder — Ollama ignores it

[[models.embeddings]]
name = "nomic-embed-text"
provider = "proxy/openai"
api_url = "http://localhost:11434/v1/embeddings"
api_key = "ollama"
```

### 3. The silent killer: a reasoning model returning empty content
With qwen3:4b every chat in the UI failed or hung. The server was healthy;
the logs showed nothing. Calling the model endpoint raw revealed the cause:

```json
{"message": {"content": "", "reasoning": "首先，用户的问题是……"},
 "finish_reason": "length"}
```

qwen3:4b is a *reasoning* model — it spent the entire token budget on hidden
chain-of-thought and returned **empty visible content** for every request.
From the UI this is indistinguishable from "the app is broken".

**Fix:** switch to a non-reasoning model (qwen2.5:3b). Verified raw before
retrying the UI:

```
Q: 用一句SQL查询表orders里有多少行
A: SELECT COUNT(*) FROM orders;
```

### 4. What a 3B model's "success" looks like
With the pipeline fully working, the warm-up question ("how many rows, how many
distinct users?") produced: a syntax error on the first generated script,
an empty-output retry, a fallback from code_interpreter to shell (`cat | head`),
20+ agent steps — and no direct numeric answer. Cloud agents (Kimi / Codex /
Julius) answered the same question in one step.

## Conclusions

- **The framework held up; the model did not.** On consumer hardware in 2026,
  model capability — not framework maturity — is the binding constraint for
  local data agents.
- **Failure modes hide below the UI.** Both root causes (missing app layer,
  reasoning-model empty content) were invisible from the browser and required
  shell access to diagnose. An agent's usefulness depends heavily on what it —
  and its operator — can actually inspect.
- Privacy and cost arguments for local deployment are real. So is the
  capability gap. Teams should benchmark their actual workload on their actual
  hardware before committing.
