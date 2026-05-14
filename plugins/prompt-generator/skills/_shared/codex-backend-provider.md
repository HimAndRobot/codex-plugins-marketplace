# Codex Backend Provider

Review Prompt uses real execution only. There is no simulated mode.

## Endpoint

- Base URL: `https://chatgpt.com/backend-api/codex`
- Endpoint: `POST /responses`
- Full default URL: `https://chatgpt.com/backend-api/codex/responses`

## Credentials

Default auth file:

```text
~/.codex/auth.json
```

Supported environment overrides:

- `CODEX_AUTH_JSON_PATH`
- `CODEX_API_KEY`
- `CHATGPT_ACCOUNT_ID`
- `CODEX_ACCOUNT_ID`
- `CODEX_BASE_URL`
- `CODEX_MODEL`

Auth resolution order:

1. Use `CODEX_API_KEY` when present.
2. Otherwise read `CODEX_AUTH_JSON_PATH` or `~/.codex/auth.json`.
3. Resolve API key from `openai_api_key`, `OPENAI_API_KEY`, `tokens.access_token`, or `tokens.accessToken`.
4. Resolve account id from env, auth file fields, token fields, or JWT payload.
5. If key or account id is missing, stop and report the missing credential.

## Request

Use Responses-style request bodies:

```json
{
  "model": "gpt-5.5",
  "instructions": "prompt variant text",
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "test case input"
        }
      ]
    }
  ],
  "store": false,
  "stream": true
}
```

Include `reasoning` only when the review configuration requires it:

```json
{
  "reasoning": {
    "effort": "medium"
  }
}
```

Required headers:

```text
Content-Type: application/json
Authorization: Bearer <api_key>
chatgpt-account-id: <account_id>
originator: prompt-generator
```

## Response Handling

Collect streamed SSE events. Extract text from `response.output_text.delta` or from the final `response.completed` / `response.incomplete` payload when deltas were not emitted.

Persist enough raw metadata in `runs.json` to debug the result, but do not store credentials.
