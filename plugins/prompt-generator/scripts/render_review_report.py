from __future__ import annotations

import argparse
import difflib
import html
import json
import re
from pathlib import Path
from typing import Any


STYLE = """
body { font-family: system-ui, sans-serif; margin: 0; color: #17202a; background: #f7f8fa; }
header { padding: 20px 28px; background: #102033; color: white; }
main { padding: 24px 28px; display: grid; gap: 18px; }
section { background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }
h1, h2, h3 { margin-top: 0; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #d9dee7; padding: 8px; vertical-align: top; }
th { background: #eef2f7; text-align: left; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f4f6f8; padding: 10px; border-radius: 6px; }
button { margin: 3px 6px 3px 0; padding: 7px 10px; border: 1px solid #bcc7d6; border-radius: 6px; background: #fff; cursor: pointer; }
button:hover { background: #eef2f7; }
.metadata-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
.metadata-grid div { border: 1px solid #d9dee7; border-radius: 6px; padding: 10px; background: #fbfcfe; }
.label { display: block; color: #5f6f85; font-size: 12px; text-transform: uppercase; }
.panel { display: none; }
.panel.active { display: block; }
.matrix-cell { min-width: 150px; }
.status { font-weight: 700; }
.diff-table { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 12px; }
.diff_add { background: #ddf4df; }
.diff_sub { background: #ffdce0; }
.diff_chg { background: #fff5b1; }
.diff_header { background: #eef2f7; }
.empty { color: #5f6f85; }
"""


SCRIPT = """
function showPanel(group, id) {
  document.querySelectorAll('[data-panel-group="' + group + '"]').forEach(el => el.classList.remove('active'));
  const panel = document.getElementById(id);
  if (panel) panel.classList.add('active');
}
"""


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def safe_id(*parts: object) -> str:
    raw = "-".join(str(part) for part in parts if part is not None)
    return re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-") or "item"


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def render_metadata(metadata: dict[str, Any], variants: list[dict[str, Any]], cases: list[dict[str, Any]]) -> str:
    values = [
        ("Prompt", metadata.get("prompt_name") or metadata.get("name")),
        ("Timestamp", metadata.get("timestamp")),
        ("Model", metadata.get("model")),
        ("Reasoning effort", metadata.get("reasoning_effort") or "unspecified"),
        ("Variant count", metadata.get("variant_count") or len(variants)),
        ("Case count", metadata.get("case_count") or len(cases)),
    ]
    cards = "\n".join(
        f"<div><span class=\"label\">{esc(label)}</span><strong>{esc(value)}</strong></div>"
        for label, value in values
    )
    return f"<section><h2>Review Metadata</h2><div class=\"metadata-grid\">{cards}</div></section>"


def render_recommendation(recommendation: dict[str, Any]) -> str:
    variant_id = recommendation.get("variant_id") or recommendation.get("best_variant") or "unspecified"
    reason = recommendation.get("reason") or recommendation.get("summary") or ""
    return (
        "<section><h2>Recommendation Summary</h2>"
        f"<p><strong>{esc(variant_id)}</strong></p>"
        f"<p>{esc(reason)}</p>"
        "</section>"
    )


def render_variants(variants: list[dict[str, Any]]) -> str:
    if not variants:
        return "<section><h2>Variant Browser</h2><p class=\"empty\">No variants supplied.</p></section>"
    buttons = []
    panels = []
    for index, variant in enumerate(variants):
        variant_id = variant.get("id") or f"variant-{index + 1}"
        panel_id = safe_id("variant", variant_id)
        active = " active" if index == 0 else ""
        buttons.append(f"<button onclick=\"showPanel('variants', '{panel_id}')\">{esc(variant_id)}</button>")
        panels.append(
            f"<div id=\"{panel_id}\" data-panel-group=\"variants\" class=\"panel{active}\">"
            f"<h3>{esc(variant_id)}</h3>"
            f"<p><strong>Change:</strong> {esc(variant.get('change_summary'))}</p>"
            f"<p><strong>Hypothesis:</strong> {esc(variant.get('hypothesis'))}</p>"
            f"<pre>{esc(variant.get('prompt'))}</pre>"
            "</div>"
        )
    return f"<section><h2>Variant Browser</h2><div>{''.join(buttons)}</div>{''.join(panels)}</section>"


def render_cases(cases: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{esc(case.get('id'))}</td>"
        f"<td>{esc(case.get('intent'))}</td>"
        f"<td><pre>{esc(case.get('input'))}</pre></td>"
        f"<td>{esc(case.get('expected_behavior'))}</td>"
        f"<td>{esc(case.get('risk_focus'))}</td>"
        "</tr>"
        for case in cases
    )
    return (
        "<section><h2>Case Browser</h2>"
        "<table><thead><tr><th>ID</th><th>Intent</th><th>Input</th><th>Expected</th><th>Risk</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def run_lookup(runs: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(run.get("variant_id") or ""), str(run.get("case_id") or "")): run
        for run in runs
    }


def render_results_matrix(variants: list[dict[str, Any]], cases: list[dict[str, Any]], runs: list[dict[str, Any]]) -> str:
    lookup = run_lookup(runs)
    header = "".join(f"<th>{esc(case.get('id'))}</th>" for case in cases)
    rows = []
    for variant in variants:
        variant_id = str(variant.get("id") or "")
        cells = []
        for case in cases:
            case_id = str(case.get("id") or "")
            run = lookup.get((variant_id, case_id), {})
            output_panel_id = safe_id("output", variant_id, case_id)
            status = run.get("response_status") or "missing"
            cells.append(
                "<td class=\"matrix-cell\">"
                f"<div class=\"status\">{esc(status)}</div>"
                f"<button onclick=\"showPanel('outputs', '{output_panel_id}')\">View output</button>"
                "</td>"
            )
        rows.append(f"<tr><th>{esc(variant_id)}</th>{''.join(cells)}</tr>")
    return (
        "<section><h2>Results Matrix</h2>"
        f"<table><thead><tr><th>Variant / Case</th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )


def render_output_viewer(runs: list[dict[str, Any]]) -> str:
    if not runs:
        return "<section><h2>Output Viewer</h2><p class=\"empty\">No run outputs supplied.</p></section>"
    buttons = []
    panels = []
    for index, run in enumerate(runs):
        variant_id = run.get("variant_id")
        case_id = run.get("case_id")
        panel_id = safe_id("output", variant_id, case_id)
        active = " active" if index == 0 else ""
        buttons.append(
            f"<button onclick=\"showPanel('outputs', '{panel_id}')\">{esc(variant_id)} / {esc(case_id)}</button>"
        )
        panels.append(
            f"<div id=\"{panel_id}\" data-panel-group=\"outputs\" class=\"panel{active}\">"
            f"<h3>{esc(variant_id)} / {esc(case_id)}</h3>"
            f"<p><strong>Status:</strong> {esc(run.get('response_status'))}</p>"
            f"<pre>{esc(run.get('output'))}</pre>"
            "</div>"
        )
    return f"<section><h2>Output Viewer</h2><div>{''.join(buttons)}</div>{''.join(panels)}</section>"


def render_diff_view(baseline_prompt: str, variants: list[dict[str, Any]]) -> str:
    if not baseline_prompt:
        return "<section><h2>Diff View</h2><p class=\"empty\">No baseline prompt supplied.</p></section>"
    buttons = []
    panels = []
    differ = difflib.HtmlDiff(wrapcolumn=100)
    for index, variant in enumerate(variants):
        variant_id = variant.get("id") or f"variant-{index + 1}"
        panel_id = safe_id("diff", variant_id)
        active = " active" if index == 0 else ""
        buttons.append(f"<button onclick=\"showPanel('diffs', '{panel_id}')\">{esc(variant_id)}</button>")
        diff = differ.make_table(
            baseline_prompt.splitlines(),
            str(variant.get("prompt") or "").splitlines(),
            fromdesc="baseline",
            todesc=esc(variant_id),
            context=True,
            numlines=3,
        )
        panels.append(f"<div id=\"{panel_id}\" data-panel-group=\"diffs\" class=\"panel{active}\">{diff}</div>")
    return f"<section><h2>Diff View</h2><div>{''.join(buttons)}</div>{''.join(panels)}</section>"


def render_diagnostics(metadata: dict[str, Any], recommendation: dict[str, Any]) -> str:
    diagnostics = metadata.get("diagnostics") or recommendation.get("diagnostics") or {}
    if isinstance(diagnostics, list):
        diagnostics = {"observations": diagnostics}
    if not isinstance(diagnostics, dict) or not diagnostics:
        return "<section><h2>Diagnostics</h2><p class=\"empty\">No diagnostics supplied.</p></section>"
    labels = [
        ("observed_strengths", "Observed Strengths"),
        ("strengths", "Strengths"),
        ("failures", "Failures"),
        ("regressions", "Regressions"),
        ("concerns", "Concerns"),
        ("observations", "Observations"),
    ]
    blocks = []
    used = set()
    for key, label in labels:
        values = as_list(diagnostics.get(key))
        if not values:
            continue
        used.add(key)
        items = "".join(f"<li>{esc(item)}</li>" for item in values)
        blocks.append(f"<h3>{esc(label)}</h3><ul>{items}</ul>")
    for key, value in diagnostics.items():
        if key in used:
            continue
        blocks.append(f"<h3>{esc(key)}</h3><pre>{esc(value)}</pre>")
    return f"<section><h2>Diagnostics</h2>{''.join(blocks)}</section>"


def render(
    metadata: dict[str, Any],
    cases: list[dict[str, Any]],
    variants: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    recommendation: dict[str, Any],
    baseline_prompt: str = "",
) -> str:
    prompt_name = metadata.get("prompt_name") or metadata.get("name") or "prompt"
    baseline = baseline_prompt or str(metadata.get("baseline_prompt") or "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Prompt Review - {esc(prompt_name)}</title>
<style>{STYLE}</style>
</head>
<body>
<header>
  <h1>Prompt Review: {esc(prompt_name)}</h1>
  <p>Model: {esc(metadata.get('model'))} | Round: {esc(metadata.get('timestamp'))}</p>
</header>
<main>
  {render_metadata(metadata, variants, cases)}
  {render_recommendation(recommendation)}
  {render_variants(variants)}
  {render_cases(cases)}
  {render_results_matrix(variants, cases, runs)}
  {render_output_viewer(runs)}
  {render_diff_view(baseline, variants)}
  {render_diagnostics(metadata, recommendation)}
</main>
<script>{SCRIPT}</script>
</body>
</html>"""


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--variants", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--recommendation", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    metadata = load_json(args.metadata)
    cases = load_json(args.cases)
    variants = load_json(args.variants)
    runs = load_json(args.runs).get("runs", [])
    recommendation = load_json(args.recommendation)
    baseline_prompt = Path(args.baseline).read_text(encoding="utf-8-sig") if args.baseline else ""
    html_text = render(metadata, cases, variants, runs, recommendation, baseline_prompt)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(html_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
