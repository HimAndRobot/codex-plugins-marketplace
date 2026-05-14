from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CODEX_AUTH_PATH = Path.home() / ".codex" / "auth.json"
DEFAULT_CODEX_BASE_URL = "https://chatgpt.com/backend-api/codex"


def _decode_jwt_payload(token: str) -> dict[str, Any] | None:
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        payload = parts[1].replace("-", "+").replace("_", "/")
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload).decode("utf-8"))
    except Exception:
        return None


def _parse_chatgpt_account_id(token: str) -> str | None:
    payload = _decode_jwt_payload(token)
    if not payload:
        return None
    nested = payload.get("https://api.openai.com/auth")
    if isinstance(nested, dict) and nested.get("chatgpt_account_id"):
        return str(nested["chatgpt_account_id"])
    return payload.get("https://api.openai.com/auth.chatgpt_account_id") or payload.get("chatgpt_account_id")


@dataclass
class Credentials:
    api_key: str
    account_id: str


def load_credentials() -> Credentials:
    env_api_key = os.getenv("CODEX_API_KEY", "").strip()
    env_account_id = (os.getenv("CHATGPT_ACCOUNT_ID") or os.getenv("CODEX_ACCOUNT_ID") or "").strip()
    if env_api_key:
        account_id = env_account_id or _parse_chatgpt_account_id(env_api_key) or ""
        if not account_id:
            raise RuntimeError("CODEX_API_KEY is set but no ChatGPT account id could be resolved.")
        return Credentials(api_key=env_api_key, account_id=account_id)

    auth_path = Path(os.getenv("CODEX_AUTH_JSON_PATH", str(DEFAULT_CODEX_AUTH_PATH)))
    if not auth_path.exists():
        raise RuntimeError(f"Codex auth file not found: {auth_path}")
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    tokens = auth.get("tokens") if isinstance(auth.get("tokens"), dict) else {}
    api_key = (
        auth.get("openai_api_key")
        or auth.get("OPENAI_API_KEY")
        or tokens.get("access_token")
        or tokens.get("accessToken")
        or ""
    )
    account_id = (
        env_account_id
        or auth.get("account_id")
        or auth.get("accountId")
        or tokens.get("account_id")
        or tokens.get("accountId")
        or _parse_chatgpt_account_id(str(api_key))
        or ""
    )
    api_key = str(api_key).strip()
    account_id = str(account_id).strip()
    if not api_key or not account_id:
        raise RuntimeError(f"Codex auth incomplete in {auth_path}")
    return Credentials(api_key=api_key, account_id=account_id)


def collect_response(base_url: str, credentials: Credentials, body: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credentials.api_key}",
            "chatgpt-account-id": credentials.account_id,
            "originator": "prompt-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        buffer = ""
        final_response: dict[str, Any] = {}
        output_items: list[dict[str, Any]] = []
        text_deltas: list[str] = []
        for raw in response:
            buffer += raw.decode("utf-8")
            while "\n\n" in buffer:
                chunk, buffer = buffer.split("\n\n", 1)
                event_name = None
                data_payload = None
                for line in chunk.splitlines():
                    if line.startswith("event: "):
                        event_name = line[7:].strip()
                    elif line.startswith("data: "):
                        data_payload = line[6:]
                if not event_name or not data_payload or data_payload == "[DONE]":
                    continue
                try:
                    payload = json.loads(data_payload)
                except json.JSONDecodeError:
                    continue
                if event_name == "response.output_text.delta":
                    delta = payload.get("delta", "")
                    if delta:
                        text_deltas.append(delta)
                elif event_name == "response.output_item.done":
                    item = payload.get("item")
                    if isinstance(item, dict):
                        output_items.append(item)
                elif event_name in {"response.completed", "response.incomplete"}:
                    final_response = payload.get("response") or {}
                    if not final_response.get("output") and output_items:
                        final_response["output"] = output_items
                    if text_deltas:
                        final_response["_collected_text"] = "".join(text_deltas)
                    return final_response
        if text_deltas:
            final_response["_collected_text"] = "".join(text_deltas)
        if not final_response.get("output") and output_items:
            final_response["output"] = output_items
        return final_response


def extract_text(response: dict[str, Any]) -> str:
    if response.get("_collected_text"):
        return str(response["_collected_text"]).strip()
    parts: list[str] = []
    for item in response.get("output", []) or []:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(str(content["text"]))
    return "".join(parts).strip()


def run_review(config: dict[str, Any]) -> dict[str, Any]:
    credentials = load_credentials()
    base_url = os.getenv("CODEX_BASE_URL", DEFAULT_CODEX_BASE_URL)
    model = os.getenv("CODEX_MODEL", "").strip() or config["model"]
    reasoning_effort = config.get("reasoning_effort")
    runs = []
    for variant in config["variants"]:
        for case in config["cases"]:
            body: dict[str, Any] = {
                "model": model,
                "instructions": variant["prompt"],
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": case["input"],
                            }
                        ],
                    }
                ],
                "store": False,
                "stream": True,
            }
            if reasoning_effort:
                body["reasoning"] = {"effort": reasoning_effort}
            response = collect_response(base_url, credentials, body)
            runs.append(
                {
                    "variant_id": variant["id"],
                    "case_id": case["id"],
                    "output": extract_text(response),
                    "response_status": response.get("status"),
                    "raw_response": response,
                }
            )
    return {"runs": runs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    result = run_review(config)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
