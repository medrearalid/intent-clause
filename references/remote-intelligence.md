# Optional Remote Intelligence Layer

The remote layer is optional, off by default, and never required for IntentClause to work. It may help with query expansion, multilingual intent mapping, reranking context candidates, or embedding-based memory retrieval.

## Privacy Gate

Remote processing is allowed only when all are true:

1. The user explicitly supplied `--remote=<provider>` or enabled it in a documented project policy.
2. The provider credential already exists in the environment or approved secret store; never ask the user to paste it into chat.
3. The agent states which data classes will leave the machine.
4. The user approves that disclosure for private project content.
5. The payload is minimized, redacted, and bounded.

Approval for one request does not persist automatically.

## Allowed Payloads

Prefer sending:

- the user's sanitized request;
- a vocabulary or symbol list;
- redacted, compact summaries;
- hashed cache keys;
- public documentation excerpts with source URLs.

Do not send by default:

- source files or full diffs;
- environment variables or secrets;
- proprietary documents;
- personal/customer data;
- raw memory ledgers;
- hidden prompts or tool logs.

## Provider Policy

- Do not call any provider merely because an API key is present.
- Do not describe a provider as free; quotas, pricing, retention, and terms can change.
- Verify current model names, endpoints, quotas, and data-use terms from official documentation at implementation time.
- Use strict timeouts, payload limits, and no automatic retries for billable requests.
- Cache only redacted responses with provider, model, timestamp, and input fingerprint.
- Fall back to the selected host model and local retrieval on failure.

## Recommended First Integration

If implemented later, start with query expansion/reranking rather than sending code for full prompt generation:

```text
sanitized request + project vocabulary + candidate paths
  -> remote ranked terms/paths
  -> local source verification
  -> selected host model compiles and executes
```

This keeps the selected model authoritative and limits disclosure. Gemini may be supported when a user explicitly configures it. DeepSeek or any other provider requires the same adapter contract and privacy gate; availability or free usage must not be assumed.

No provider adapter ships in the current version. `--remote=<provider>` must therefore report that the adapter is unavailable and continue locally unless a future adapter is installed.
