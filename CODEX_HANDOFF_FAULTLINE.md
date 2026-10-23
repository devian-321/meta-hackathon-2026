# CODEX HANDOFF — FaultLine CI (GitLab) + FaultLine Lab (Meta) + FaultLine-Tune (Lexsi)

**Prepared:** October 23, 2026 (India / IST)  
**Owner:** Individual developer entering hackathons solo  
**Immediate focus:** Ship a real, compelling **GitLab Life After Code** submission by **October 27, 2026, 13:00 UTC = 18:30 IST**.  
**Instructions to Codex:** Treat this as a product and implementation brief, not a record of completed work. Inspect the local environment first. Do not invent implemented features, GitLab access, API behavior, results, or links. Work in small tested increments. When details are missing, make safe, explicit assumptions and move forward with local work; flag blockers rather than pretending that integrations succeeded.

---

## 1. User goal and context

The user wants to **win or place highly at globally recognized AI hackathons as a solo developer**, with projects that also signal serious technical skill on their résumé. Their highest-priority events:

1. **GitLab Transcend / Life After Code** — emergency priority, currently preparing the Devpost submission, project name already entered as **FaultLine CI**. Deadline **Oct 27, 2026, 18:30 IST**. Approximately four calendar days from Oct 23. User has joined/started Devpost entry, but **GitLab Transcend contributor provisioning / Duo Agent Platform access has NOT been confirmed**.
2. **Meta Global AI Developer Hackathon** — planned **Indie Developer track**, Oct 26–Nov 4 (event times in ET; deadline Nov 4 21:00 ET, or Nov 5 07:30 IST if Eastern Daylight Time applies on Nov 4? NOTE: US Eastern switches from EDT to EST on Nov 1; Nov 4 21:00 EST = Nov 5 07:30 IST). User has been preparing an application; acceptance not confirmed. User wants a technically ambitious but demonstrable project rather than an LLM wrapper. The full official rules were expected Oct 26. The competition describes Muse Spark / Muse Wonder / Muse Image / SAM 3.1, Meta Model API, and open weights. Do not assume model access or features until verified.
3. **Lexsi AI Safety & Alignment Hackathon** — user saw a registration form, advised to prefer **Agentic Fine-tuning**. Concept named **FaultLine-Tune**. Whether signed up successfully is unknown. This requires actual post-training/evaluation, not simply prompt engineering.

User has past experience building a **voice AI bot with Microsoft AutoGen and Temporal** (agent coordination + durable workflow orchestration). Exact implementation, reliability features, and speech technologies are unverified. They have worked with Flutter, Git, and a separate personal project called **Maestro** in a `step-2b-simulator` branch, but do NOT assume that Maestro provides an already-working simulator. Do NOT reuse employer code, credentials, or private assets.

The user's personal GitHub alias was `github-personal`, with a repo reference like `devian-321/Maestro-tech`. For this hackathon, the required **public GitLab** repo is the canonical submission repo. Never assume a current working remote, active branch, or Git credential state; inspect the actual repo.

The user uses macOS and **fish shell**, and sometimes works from an office laptop. Respect project-specific personal Git identity and avoid accidentally pushing to company remotes. Inspect `git remote -v`, `git status`, and local vs global identity BEFORE changing or pushing any Git configuration.

---

## 2. The product in one sentence

**FaultLine CI** is a reproducible, explainable **CI/CD failure-injection and AI recovery system** that uses the **GitLab Duo Agent Platform** to diagnose failing pipelines, recommend or execute safe fixes, rerun tests, and independently verify the recovery.

Draft elevator pitch already entered or proposed for Devpost:

> FaultLine CI turns broken pipelines into self-healing workflows. Powered by GitLab Duo agents, it diagnoses CI/CD failures, proposes fixes, and verifies recovery through automated testing.

That sentence is **aspirational until implemented**; the final submission text must reflect what actually works.

**Why it matters:** CI failure recovery is painful and often opaque; existing automated fix tools may claim success without validating the outcome. FaultLine's differentiator should be **replayable incident scenarios, causal evidence, safe approval gates, outcome validation, and side-by-side trace comparison**, rather than a generic “AI fixes CI” wrapper.

**What judges should see in 2–3 minutes:**
1. A GitLab repo has a green baseline.
2. A controlled code change or fault makes a real GitLab pipeline fail.
3. GitLab Duo agent/flow analyzes the failing job and produces a diagnosis and proposed change (or safely executes it if the chosen autonomy level supports that).
4. A corrected commit/MR or approved patch triggers a rerun.
5. Real CI turns green, and a deterministic **independent verifier** checks actual results, not the agent's own self-description.
6. UI or readable report shows root cause, actions, timestamps, safety approvals, before/after pipeline IDs, outcomes, and latency/tool-call counts when truly observable.

**Non-negotiable:** The GitLab Duo Agent Platform MUST execute a meaningful part of this workflow. A local Python agent with a GitLab logo and mocked AI invocation would not qualify.

---

## 3. Verified GitLab Life After Code event rules (as of Oct 23, 2026)

Authoritative sources (open these / recheck if possible):
- Event: https://gitlab-transcend.devpost.com/
- Official rules: https://gitlab-transcend.devpost.com/rules
- Resources and FAQ: https://gitlab-transcend.devpost.com/resources
- Contributor onboarding: https://contributors.gitlab.com/transcend-hackathon
- Duo platform quickstart: https://docs.gitlab.com/user/get_started/get_started_agent_platform/
- Built-in CI Expert Agent: https://docs.gitlab.com/user/duo_agent_platform/agents/foundational_agents/ci_expert_agent/
- Built-in Fix CI/CD Pipeline Flow: https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/fix_pipeline/

**Dates:** Oct 5–Oct 27 submission period; closes **Oct 27, 13:00 UTC = 18:30 IST**. Judging Oct 28–Nov 14; winners on/around Nov 16.

**Choose Path A: Start Fresh** as the default, IF creating new code for this hackathon on/after Oct 5. Build an app, real CI/CD pipeline, and automation from scratch; deployment not required. **Path B: Bring Your Own** only if importing an existing original **MIT-licensed** public project; requires NEW post-code automation and live deployment on/after Oct 5 and extra original-repo/deployment URLs. Do not accidentally use an old personal repo and call it Path A.

**Autonomy:** Assisted = approvals at each step; Supervised = agent handles multi-step workflow but user approves outcome; Hands-off = runs through to production without human intervention. Default target for short timeline is **Assisted** or **Supervised**, with category chosen from actual behavior rather than ambition. Approval before modifying protected branches is good engineering. We do NOT need a dangerous hands-off mode to look impressive.

**Required:**
- Meaningful GitLab **Duo Agent Platform** use (agents/flows/MCP clients), beyond ordinary API calls.
- **Public GitLab repository** with all code, run steps, assets; root-level **MIT LICENSE** recognized in GitLab About section.
- Visible **GitLab CI/CD pipeline history** showing automation run.
- Clear project description and working demonstration.
- **YouTube video under 3 minutes**, Public or Unlisted, showing actual project functionality. No unlicensed copyrighted music or assets.
- For Path B: original MIT project URL, actual deployed live URL, and evidence new automation and deployment were created during submission window.
- No changes to submitted repo, linked demo, or submission during judging after deadline; **fork/copy** to continue Meta work.
- User needs contributor onboarding; GitLab reports provisioning takes about **24 business hours**. Event FAQ says participants get **500 GitLab Credits/month** and need the **Developer + AI** role. Check access immediately.
- Optional Google Cloud deployment may add up to **0.2 judging points**, requires live URL and deployment code, but it is NOT essential; don't spend critical time on this unless MVP is solid.
- Judging: Stage 1 theme and Duo use pass/fail; Stage 2 equally weighted technical implementation, design/coherent end-to-end workflow, potential impact, innovation, presentation. Lifecycle stages include plan, create, verify, package, secure, release, configure, monitor, govern. Meaningful breadth is desirable, but do not fake stage coverage.

**Important originality consideration:** GitLab's official docs already include a **Fix CI/CD Pipeline Flow** and a **CI Expert Agent**. A plain replica of their built-in demonstration is weak. Build extra value in test scenario generation, differential replay, independently verified outcome reports, and/or cross-stage check integration. First verify what the built-ins actually can do; don't assume undocumented webhooks, permission scopes or API endpoints.

---

## 4. The precise GitLab MVP (must ship first)

### Story A — Single reproducible failure and recovery (P0)

Given a simple Python application with a known-good unit test suite:
- `main` contains working code, tested by a real `.gitlab-ci.yml` pipeline.
- A controlled failure scenario introduces a deterministic bug (e.g. arithmetic logic regression, missing function branch, malformed dependency configuration) on a branch; CI fails visibly.
- GitLab Duo analyzes the failed pipeline and proposes a concrete code fix via agent/flow.
- A human approves fix if in Assisted mode; code change is committed in a separate branch/MR (not direct unsafe write to default branch).
- A real pipeline rerun succeeds.
- Independent verifier checks actual GitLab pipeline/job status and actual test output, records both old and new pipeline IDs + evidence URLs, declares PASS only if verifiable.
- The whole chain is **repeatable** from clean instructions; no hidden manual step is disguised as agent action.

### Story B — Explanation / incident report (P0)

Generate a readable structured report (JSON + Markdown, or minimal web page) with:
`scenario_id`, fault_type, GitLab project path, failing commit SHA, failing pipeline URL, failure evidence, agent diagnosis, proposed fix or MR URL, approval state, rerun pipeline URL, observed verification, final result, and whether data was mocked or real. Redact secrets.

### Story C — Baseline vs recovered execution (P1)

Show what a non-recovering baseline does vs AI-assisted recovery for the same failure, using consistent conditions. Compare verified completion and steps/time only if genuinely measured. No invented success-rate percentages. Include deterministic, seeded failure-scenario fixture and the raw evidence.

### Story D — 2nd or 3rd fault category (P1)

Examples: test assertion regression, invalid package/lockfile, transient API outage (harder to demonstrate deterministically). Prefer two **different causal failures** if it does not destabilize P0. Distinguish a true code bug from a transient infra fault; do not propose blindly retrying a deterministic bug.

### Story E — UI and extras (P2)

Only after P0 works: simple Streamlit/React/Svelte dashboard; timeline of pipeline failure -> diagnosis -> proposal -> approval -> re-run -> verified recovery. Optional GitLab issue comment or security scan for another DevSecOps stage. Cloud deploy is a stretch goal, not a P0 requirement.

### Explicit non-goals for the four-day sprint

No generalized multi-agent runtime, no multi-tenant SaaS, no Kafka/Kubernetes, no ML training, no arbitrary production deployment, no complex authentication portal, no elaborate CSS dashboard, no full observability platform, no costly GPU provisioning. Temporal and AutoGen are **past user experience**, not requirements for this P0 implementation. Only add them if there is a clearly demonstrated benefit and time permits.

---

## 5. Proposed engineering architecture (adapt to actual GitLab interfaces)

```
GitLab Push / MR
       |
       v
Real .gitlab-ci.yml -> failing tests / job logs
       |
       v
GitLab Duo Agent/Flow (native GitLab feature)
       |  diagnosis and (with appropriate approval) patch or MR
       v
Fix proposal / approval gate
       |
       v
Real GitLab CI rerun
       |
       v
Independent verifier reads pipeline state and test evidence
       |
       v
Trace + comparison report (Markdown/JSON; UI only if time)
```

### Suggested repository layout

```
faultline-ci/
  README.md
  LICENSE
  .gitlab-ci.yml
  pyproject.toml
  .env.example
  src/faultline_ci/
    __init__.py
    scenarios.py          # seeded, controlled fault scenarios / metadata
    gitlab_client.py      # authenticated GitLab API read/write with safety
    traces.py             # structured, redacted event records
    verifier.py           # independent actual-outcome verification
    report.py             # Markdown/JSON evidence report
  sample_app/
    ...                   # intentionally small and testable demo application
  tests/
    test_sample_app.py
    test_fault_scenarios.py
    test_verifier.py
  demo/
    script.md
    proof/                # sanitized run IDs, screenshots, report files
  docs/
    architecture.md
    decisions.md
    hackathon-compliance.md
    deployment.md        # only if actually deployed
  ... GitLab Duo agent/flow configs in paths REQUIRED by CURRENT official docs ...
```

This is a **suggested** layout, NOT a claim about the real Duo config path. Confirm from GitLab current docs. Prefer a small dependency set: Python, pytest, requests/httpx, official GitLab integration as appropriate; native Duo configs. Use Pydantic only if beneficial. Avoid using unnecessary third-party LLM services when native Duo must be demonstrated.

**Safety / trust properties:**
- Never execute untrusted CI log text as shell commands. Treat it as data.
- Keep secrets in masked/protected GitLab CI/CD variables / local env, not in files or traces.
- Limit GitLab token scopes to minimum; never print tokens.
- Limit auto-fixes to an allowlisted demo directory / branch; require approval for high-impact changes.
- Require independent objective PASS status (GitLab successful pipeline PLUS tests) before saying recovered.
- Use idempotency keys/guards for jobs and replays so repeated webhook events do not cause loops.
- Prevent infinite repair retries with bounded attempts, e.g. max 2 (configurable).
- Include timestamps and scenario IDs to distinguish demos from screenshots from previous runs.
- Don't misrepresent a mocked local demo as a working GitLab Duo execution.

---

## 6. Suggested implementation schedule (minimum viable first)

**Oct 23 evening:**
- Inspect repo/folders and Git identity; make sure personal, not company remote.
- Check Devpost project draft exists; verify GitLab Contributor Platform onboarding and Duo access, role/credits.
- Choose Path A + Assisted provisionally; write technical acceptance checklist.
- Create new GitLab project and MIT license as access allows; scaffold small Python app with a deliberately reproducible broken branch and working `.gitlab-ci.yml`.
- End first session with **real red pipeline** and screenshot/log, even if Duo access pending.

**Oct 24:**
- Get Duo onboarding and quickstart working.
- Inspect and invoke a native GitLab Duo agent/flow on a failing pipeline.
- Commit actual agent/flow configuration and reproducible setup notes.

**Oct 25:**
- Complete diagnosis -> fix proposal/MR -> human approval -> CI re-run -> independent verification. Export evidence report.
- Add a second fault type only if first end-to-end path is stable.

**Oct 26:**
- QA from clean clone. Tighten permissions, docs, error handling.
- Capture <3m YouTube demo in real project with visible failed and successful pipeline IDs.
- Fill Devpost project story, tag technologies actually used, provide URLs, attach video.

**Oct 27 (BEFORE 18:30 IST):**
- Early final submission, not last-minute. Verify public repo/LICENSE/history/video, category/Path accuracy, devpost submit confirmation.
- Freeze GitLab submission repository and linked media for judging. Fork/copy if continuing.

This is an aggressive schedule, not a guarantee. If Duo provisioning takes longer, keep improving reproducible CI test harness and docs; don't fake a GitLab integration.

---

## 7. Objective done criteria (submission quality bar)

**P0 done only when all checked:**
- [ ] App + tests run locally from documented clean setup.
- [ ] A deliberate, safe change causes an actual GitLab CI pipeline to fail.
- [ ] An authentic GitLab Duo Agent Platform agent/flow meaningfully diagnoses or coordinates remediation.
- [ ] Proposed correction is reviewable; changes are traceable to commit/MR.
- [ ] Test rerun is an actual GitLab job/pipeline; result is observable and independently verified.
- [ ] Replay/trace evidence includes actual GitLab links, non-secret IDs, diagnosis and outcome.
- [ ] No fabricated metrics, tests, screenshots, demos or links.
- [ ] MIT-licensed PUBLIC GitLab repo, valid readable README, visible pipeline history.
- [ ] Public or unlisted YouTube demo <3 min, actual functionality, no copyrighted material.
- [ ] Devpost submission accurately maps completed features to the chosen Path and autonomy category.
- [ ] All URLs and code remain accessible during judging; submitted repo/version is frozen after deadline.

**Demonstration narrative (2:30 target):**
- 0:00–0:15: “A green pipeline turns red. Most CI bots guess at a fix. FaultLine proves the fix worked.”
- 0:15–0:40: Show initial green + controlled breaking commit / actual failing pipeline.
- 0:40–1:30: Show authentic GitLab Duo agent/flow diagnosis + reviewable repair proposal + approval (if Assisted).
- 1:30–2:10: Show actual rerun green; independent verifier compares IDs, job/test signals.
- 2:10–2:30: Show trace/report, claim only measurements actually collected, say what makes this different.

---

## 8. Meta expansion (only after GitLab submitted; verify final Oct 26 rules)

**FaultLine Lab:** an agent reliability / fault injection and recovery benchmarking environment for software agent workflows, using Meta models where appropriate. Independently verifiable work product is a key differentiator. Proposed high-level architecture:

```
User task -> sandboxed tool/API agent runner -> deterministic fault injector
          -> policy-aware recovery planner (Meta models)
          -> executor -> independent evaluator -> reproducible replay dashboard
```

Themes: **Push the Frontier** (agent reliability in software systems), potentially **Build for Your World** if backed by lived developer experience. Proposed observables: task success rate, error classification accuracy, recovery success, tool calls, cost, latency; collect controlled data, don't invent numbers. Build within the official Meta competition window, adhering to its newly published rules and API/model access/geo constraints. **Do not alter the GitLab submitted repo or copy restricted code/assets**. A conceptual overlap is fine in planning; whether and how prior code is reusable depends on Meta rules, licensing and new-work requirements. Separate repo and Git history.

We earlier considered **Repro**, turning mobile bug recordings into reproducible tests, and **WorldModel Studio**, but chose FaultLine because it aligns with user's orchestration background and is feasible for a solo developer in ~10 days. The choice is provisional if working evidence suggests a stronger angle.

Meta application drafted around FaultLine; actual selection status unknown. User was advised to submit to **Indie Developer track**.

---

## 9. Lexsi expansion (future independent project)

**FaultLine-Tune:** train an open-weight model to more reliably handle tool failure recovery, with actual post-training and measurable baseline comparison. User selected/was advised **Agentic Fine-tuning** track. Proposed capabilities:

- Construct or curate a small, safe dataset of tool-call + recovery trajectories from controlled simulation.
- Define train/test split carefully to avoid leakage.
- Apply a real LoRA/QLoRA/SFT post-training technique if eligible under Lexsi rules, preferably through required event tools (earlier discussion mentioned AgentTune/AuditKIT; VERIFY current tools/rules before coding).
- Evaluate **before vs after** on unseen fault scenarios, actual completion, tool validity, unnecessary calls, recovery success; disclose limitations.
- Keep code, training artifacts, license, and evidence separate according to event rules; do not submit the same code unchanged across events unless explicitly allowed.

User's self-assessed experience with fine-tuning and red-teaming was NOT confirmed. Do not imply they have done post-training in past simply because this project intends to do it.

---

## 10. Devpost field context

The user has already started a GitLab Devpost draft titled **FaultLine CI**; screenshots show fields:
- **Project name:** FaultLine CI
- **Elevator pitch:** preliminary text above; adjustable before deadline.
- **Project story:** “About the project” (inspiration, what was learned, build process, challenges) supports Markdown.
- **Built with:** accurate tags for technologies actually used.
- **Try it out:** public GitLab repo and/or real deployed URL.
- **Project media:** screenshots, video etc.

User decided **to write final detailed submission text after implementing**, not beforehand. Codex should maintain `docs/submission-notes.md` as live evidence, separating **implemented**, **tested**, **planned**, **blocked**. Later this can become a truthful Devpost write-up.

Do not claim “fixed automatically”, “self-healing”, “N% reliability improvement”, “fully autonomous” or “production-grade” unless code, traces and recorded evidence support each phrase.

---

## 11. Start here: exact first action requested from Codex

**First, orient. Don't jump straight to a huge multi-agent platform.**

1. Inspect current directory, `git status`, `git remote -v`, local Git identity, README, and any existing `.gitlab-ci.yml`. Do not destroy existing files or change remotes without permission. Identify whether this is the correct *new GitLab competition project*. If not, scaffold a new clearly named folder for FaultLine CI.
2. Read authoritative GitLab Duo Agent Platform quickstart and built-in pipeline flow docs and find the **smallest supported native agent/flow integration** that can work given real access. Confirm event onboarding / credentials with user if needed, but keep working on local CI fixture meanwhile.
3. Report a **concise implementation plan** with exact stack, P0 milestone and current blockers. If environment supports file edits, implement immediately rather than only proposing architecture.
4. Build **one tiny testable Python repo + pytest + `.gitlab-ci.yml`** with a deterministic scenario that demonstrably produces a failing pipeline. Make passing tests stay green on main; place fault on separate demo branch.
5. Integrate one REAL GitLab Duo agent/flow with that failure, then implement independent verification using real GitLab pipeline state; store redacted evidence.
6. Run tests and document exact commands/results. End each coding increment with which files changed, what passed, what still requires actual GitLab access.

**Preference ordering:** working real integration > explainable verified result > reproducibility > visuals > extras.

**Policy for missing access:** do not store auth tokens in repo; ask only for actionable permissions/token scopes/host URLs (not raw secrets in chat). Never write fake CI run links. Use local stubs to test parsing while clearly marking them simulated; final submission must demonstrate real Duo and real GitLab CI.

---

## 12. Useful official links / constraints to keep handy

- GitLab overview: https://gitlab-transcend.devpost.com/
- GitLab official rules: https://gitlab-transcend.devpost.com/rules
- GitLab resources / FAQ: https://gitlab-transcend.devpost.com/resources
- GitLab contributor onboarding: https://contributors.gitlab.com/transcend-hackathon
- GitLab agent platform quickstart: https://docs.gitlab.com/user/get_started/get_started_agent_platform/
- GitLab CI Expert Agent: https://docs.gitlab.com/user/duo_agent_platform/agents/foundational_agents/ci_expert_agent/
- GitLab Fix Pipeline Flow: https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/fix_pipeline/
- Meta event / waiver (rules scheduled for Oct 26): https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver
- Lexsi: https://hackathon.lexsi.ai/

**Final message for Codex:** This user is time constrained and competitive. Produce a genuinely functioning, legally eligible hackathon entry rather than endless discussion. Be ambitious about quality, ruthless about scope, and scrupulously factual about what has actually been built.
