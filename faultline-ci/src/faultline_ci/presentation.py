"""Dependency-free HTML view over an evidence report, with escaped data."""

from html import escape
from typing import Any


def render_html(report: dict[str, Any], markdown: str) -> str:
    local = report.get("source") == "local_subprocess"
    title = "Local recovery rehearsal" if local else "GitLab evidence report"
    notice = (
        "Scripted local repair. GitLab Duo and hosted pipelines were not run."
        if local
        else "GitLab API evidence. Duo provenance and human approval need separate review."
    )
    verification = report.get("verification", {})
    passed = isinstance(verification, dict) and verification.get("passed") is True
    outcome = "PASS" if passed else "FAIL / INCOMPLETE"
    rows = []
    if local:
        for run in report.get("local_runs", []):
            values = [
                run["stage"],
                run["tests"] - run["failed"],
                run["failed"],
                str(run["commit_sha"])[:12],
            ]
            rows.append(
                "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in values) + "</tr>"
            )
        headers = ["Execution stage", "Passing tests", "Failing tests", "Commit"]
    else:
        headers = ["Pipeline", "Status", "Tests", "Commit"]
        for stage in ("before", "after"):
            pipeline = report.get(stage, {})
            values = [
                f"{stage}: {pipeline.get('pipeline_id', 'missing')}",
                pipeline.get("status", "missing"),
                len(pipeline.get("tests", [])),
                str(pipeline.get("sha", ""))[:12],
            ]
            rows.append(
                "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in values) + "</tr>"
            )
    headings = "".join(f"<th>{heading}</th>" for heading in headers)
    guard = report.get("repair_verification", {})
    guard_passed = isinstance(guard, dict) and guard.get("passed") is True
    guard_label = "PASS" if guard_passed else "FAILED / NOT CHECKED"
    downloads = '<a href="recovery.json">JSON evidence</a><a href="recovery.md">Markdown report</a>'
    if local:
        downloads += '<a href="demo.bundle">Git proof bundle</a>'
    rejected = report.get("tampered_verification", {}).get("passed") is False
    tampering_card = (
        '<div class="card"><span class="label">False-green attempt</span>'
        f"<strong>{'REJECTED' if rejected else 'NOT REJECTED'}</strong></div>"
        if local
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FaultLine CI · {title}</title>
<style>
:root{{color-scheme:light;
font:16px/1.6 system-ui,sans-serif;
color:#182338;
background:#eef2f6}}
*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1120px;
margin:auto;
padding:40px 24px}}
header{{background:#111d31;
color:#fff;
padding:32px;
border-radius:20px}}h1{{font-size:clamp(30px,5vw,46px);
line-height:1.15;
margin:12px 0}}
.eyebrow{{letter-spacing:.16em;
text-transform:uppercase;
font-size:12px;
color:#91bdff}}
.notice{{background:#fff1cd;
border-left:5px solid #ac6b00;
padding:16px 20px;
margin:24px 0;
border-radius:8px}}
.cards{{display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:16px;
margin:24px 0}}
.card,section{{background:#fff;
padding:24px;
border:1px solid #d5dee8;
border-radius:14px}}
.card strong{{display:block;
font-size:22px;
margin:8px 0}}.label{{font-size:13px;
color:#53657d}}
.ok{{color:#146242}}.pending{{color:#855000}}section{{margin:20px 0}}h2{{font-size:20px;
margin-top:0}}
.table-wrap{{overflow-x:auto}}table{{width:100%;
border-collapse:collapse;
text-align:left;
font-size:14px}}
th,td{{padding:14px 12px;
border-bottom:1px solid #e3e9f0}}th{{color:#53657d}}
pre{{white-space:pre-wrap;
overflow-wrap:anywhere;
font:13px/1.7 ui-monospace,monospace}}
nav{{display:flex;
gap:12px;
flex-wrap:wrap}}a{{padding:10px 16px;
color:#164e9b;
background:#eaf2ff;
border-radius:8px;
text-decoration:none}}
footer{{font-size:13px;
color:#53657d;
margin-top:24px}}details summary{{cursor:pointer;
font-weight:600}}
</style>
</head>
<body>
<main>
<header>
<span class="eyebrow">FaultLine CI · reproducible recovery evidence</span>
<h1>{title}</h1>
<p>Observe the failure. Inspect the correction. Check the work.</p>
</header>
<p class="notice">{escape(notice)}</p>
<div class="cards">
<div class="card">
<span class="label">Requested checks</span>
<strong>{outcome}</strong>
</div>
<div class="card">
<span class="label">Repository repair guard</span>
<strong>{guard_label}</strong>
</div>
{tampering_card}
<div class="card">
<span class="label">Native Duo execution</span>
<strong class="pending">Not verified</strong>
</div>
</div>
<section>
<h2>Observed execution</h2>
<div class="table-wrap">
<table>
<thead>
<tr>{headings}</tr>
</thead>
<tbody>{"".join(rows)}</tbody>
</table>
</div>
</section>
<section>
<h2>Evidence bundle</h2>
<nav>{downloads}</nav>
<p>Check the source and scope before interpreting a PASS.</p>
<details>
<summary>Read the full report</summary>
<pre>{escape(markdown)}</pre>
</details>
</section>
<footer>No agent's self-description is treated as proof.
This report does not establish production readiness.</footer>
</main>
</body>
</html>"""
