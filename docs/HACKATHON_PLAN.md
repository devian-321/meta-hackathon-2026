# FaultLine delivery plan

Researched October 23, 2026. Priority updated to GitLab first following the owner's
explicit instruction. This is a plan and evidence ledger, not a claim of live integrations.

## Delivery decision

Ship **FaultLine CI** for GitLab by October 27. Keep **FaultLine-Tune** as a separately
scoped November project. Keep **FaultLine Lab** conditional on Meta acceptance and final
rules. One developer owns all three; these are separate entries with related research,
not an assumption that one unchanged submission is eligible everywhere.

The current checkout is a GitHub Meta placeholder. GitLab deliverable files live in
`faultline-ci/` until transferred to the contributor-provisioned project root. Do not push
the planning workspace as if it were already the canonical GitLab submission. No remote
or identity has been changed. A personal commit email must be established before commits.

## Research register

Read primary sources; recheck them before submission because organizers can revise rules.

| Subject | Verified finding | Source |
| --- | --- | --- |
| GitLab deadline | Oct 27, 13:00 UTC / 18:30 IST | [Event](https://gitlab-transcend.devpost.com/) |
| GitLab route | Path A supports newly built work; choose autonomy from observed behavior | [Rules](https://gitlab-transcend.devpost.com/rules) |
| GitLab deliverables | Public MIT GitLab source, visible CI history, English materials, working video under 3 minutes on YouTube | [Rules](https://gitlab-transcend.devpost.com/rules) |
| GitLab access | Contributor provisioning takes about 24 business hours; event role is Developer + AI, with 500 monthly credits | [FAQ](https://gitlab-transcend.devpost.com/resources) |
| GitLab freeze | Leave submitted code, video and linked materials unchanged during judging; continue in a copy | [FAQ](https://gitlab-transcend.devpost.com/resources) |
| Native repair | UI flow proposes inline fixes or a repair MR according to context; session evidence is available | [Fix Pipeline](https://docs.gitlab.com/ci/pipelines/fix_pipeline/) |
| Agent execution | `.gitlab/duo/agent-config.yml` is read from the default branch | [Execution configuration](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/) |
| GitLab evidence | Pipeline details/test reports and paginated job lists are documented REST interfaces | [Pipelines](https://docs.gitlab.com/api/pipelines/), [Jobs](https://docs.gitlab.com/api/jobs/) |
| Lexsi timeline | Register by Nov 5; initial submission Nov 14 end of day; shortlisted extension through Nov 21; Demo Day Nov 22 | [Lexsi](https://hackathon.lexsi.ai/) |
| Lexsi constraints | Build during event, Cohere dense open weights, HF artifacts, multiple before/after metrics and HF article; track 3 has an exception to the two-repository minimum | [Lexsi rules](https://hackathon.lexsi.ai/#rules) |
| Meta status | Selection required; applications close Oct 25 23:59 ET or earlier at capacity; decisions by Oct 26 09:00 ET; full rules due before kickoff | [Organizer](https://events.cerebralvalley.ai/e/meta-ai-developer-hackathon) |

### Corrections and unresolved facts

- GitLab's old repair-flow URL redirects to the CI documentation. The flow is UI-only;
  do not invent a REST endpoint to start it. The first implementation uses an explicit UI
  invocation and records that human step.
- Built-in flow behavior can differ with deployed version and settings. Observe whether
  the provisioned instance produces suggestions or a new MR before writing the demo.
- The official GitLab rules allow OSI-approved third-party components with compatible
  licenses; the FAQ's broad MIT phrasing is less precise. Our own source is MIT. Maintain
  dependency notices and check compatibility; seek organizer clarification if needed.
- Lexsi's large Nov 1–21 banner is not the initial submission deadline. Timezone for
  “end of day” on Nov 14 is unspecified on the page; ask organizers and target Nov 13.
- Lexsi requires a Cohere model; “any open-weight model” in the handoff is too broad.
- Meta's header uses EST while its schedule says ET. Nov 4, 21:00 New York time converts
  to Nov 5, 07:30 IST. Confirm final portal timezone; set an internal earlier cutoff.
- No private registration, acceptance, GitLab entitlement, runner availability, GPU credit,
  or model access has been verified. Public research cannot establish account status.

## GitLab product and implementation

**User:** a developer reviewing an AI-proposed CI repair.
**Promise:** show exactly which failure was reproduced and whether the expected tests
passed on the intended repair commit. Keep diagnosis, approval and outcome as separate facts.

**P0 scenario:** an invoice-pricing regression changes discount subtraction to addition.
The invoice tests include no discount, fractional-cent rounding, full discount, and invalid
inputs. The unchanged tests fail deterministically. A proposal that deletes the assertions,
skips a failing case, or disables the test job must not qualify as a repair.

### Components and boundaries

| Component | Responsibility | Forbidden shortcut |
| --- | --- | --- |
| Sample app | Small integer-money calculation with explicit input contract | Hide the failure behind flaky services |
| Scenario exporter | Copy controlled fixtures and alter one known expression | Modify the current branch invisibly |
| GitLab CI | Quality checks, sample JUnit output, harness tests | Mark failing tests `allow_failure` |
| Native Duo flow | Diagnose and propose a reviewable repair | Substitute a different local model |
| Human review | Approve allowed file changes; record actual decision | Claim approval was automatic |
| Read-only API client | Fetch actual pipeline/job/test results with bounded requests | Execute commands obtained from logs |
| Independent verifier | Check pipeline identity, expected SHA and original test identities/results | Trust the agent's “fixed” message |
| Evidence renderer | Export timestamped JSON and Markdown | Invent latency, agent actions or links |

The CLI/API adapter has no write operations. Token scope is `read_api` for evidence reading;
Git push authentication and Duo permissions are separate. For the first demo, restrict repair
review to `sample_app/pricing.py`; changes to CI, tests, dependencies, verifier, or agent
instructions require rejection/escalation. Repository instructions guide the agent but do
not enforce authorization. Enforce the boundary through actual review and branch protection.

Use Python 3.12 and uv with committed lockfile. Pytest covers business behavior, controlled
faults, API parsing and false-green rejection; Ruff checks style/imports; mypy checks core
types. No frontend framework, workflow engine or database is needed for the first loop.
After live recovery works, render the same evidence into a compact static report if it
helps presentation. A hosted interactive application is optional for Path A.

### P0 backlog and acceptance gates

1. **Foundation:** MIT license, clean install, lockfile, tests and documented commands.
   Local baseline must pass; exported fault must fail only the intended sample assertions.
2. **GitLab baseline:** place deliverable at provisioned repo root; confirm project public,
   runner enabled and default branch protected. Observe a real green pipeline and retain URL/SHA.
3. **Red incident:** create `demo/pricing-discount-sign-v1`, change only pricing expression,
   open a draft MR and record failed pipeline and sample-test JUnit. Keep main green.
4. **Duo remediation:** invoke native flow; capture session URL, root-cause explanation,
   suggestions/MR, timestamps, proposed diff and human review outcome.
5. **Independent proof:** read before/after API evidence. Require failed initial pipeline,
   distinct newer successful pipeline, expected full repair SHA, successful sample job,
   and original test identities restored without skipping. Missing evidence fails closed.
6. **Trust hardening:** connect repair to fault ancestry, inspect full diff, reject CI/test
   tampering, and record a tampered-repair rejection. These extend outcome checking;
   they are not implemented merely because the initial verifier passes unit tests.
7. **Reproduction:** clean clone and exact runbook reproduce green → red → review → green.
   Save sanitized evidence; verify judge access without signing in.
8. **Presentation:** evidence report, readable README, architecture/limitations, screenshots,
   narrated 2:35 video, final truthful Devpost story and checked public URLs.

The initial API verifier proves a narrower property than complete causal recovery. It
does not yet establish ancestry, inspect diffs, validate scenario ID against remote code,
or authenticate the Duo session/approval. Until those are connected, its PASS means only
that the collected outcome checks passed. The final incident report needs all those links.

### Time budget, IST

| Date | Target | Cut decision |
| --- | --- | --- |
| Oct 23 evening | Local baseline/fault/verifier; start or confirm onboarding | Access dependency raised immediately |
| Oct 24 | Public GitLab green/red history; first meaningful Duo diagnosis | By evening, escalate missing access via event support; no fake fallback |
| Oct 25 | Reviewable repair, green rerun, independent evidence; reject tampering | Stop feature expansion until one loop works |
| Oct 26 morning | Clean-clone QA, final report and docs | Second scenario only if P0 stable |
| Oct 26 afternoon/evening | Capture real runs and edit/narrate video; Devpost draft | Drop dashboard/cloud before sacrificing proof |
| Oct 27 by 12:00 | Internal submission target; incognito link checks and receipt | Keep 6.5-hour buffer before 18:30 deadline |
| After submitting | Archive SHA/report/video metadata; freeze submitted assets | Continue other events only in separate repositories |

If access is delayed, keep local quality/replay work moving. A local demo alone cannot
satisfy the Duo gate. Once access exists, prioritize one native diagnosis and validated
reviewed repair over extra categories. Use Assisted provisionally; confirm that each
meaningful action actually has approval before selecting it on the submission form.

### Quality and repository contract

- Small cohesive modules; typed public boundaries; explicit errors and return codes.
- Commit only coherent reviewed increments after local checks. Use personal project-local
  Git identity and DCO sign-off after the owner confirms their personal email.
- Lock dependencies; review new packages and licenses. Never commit caches, virtualenvs,
  tokens, raw account exports or private work code.
- Keep tests, scenario definitions and verification logic outside the allowed repair path.
- Document trust assumptions, unsupported cases, unavailable access and actual test results.
- Bound network requests and repair attempts. No polling service or automatic retry loop in
  P0; if added later, cap at two reviewed attempts and deduplicate by incident/commit.
- Unit/API transport tests are synthetic; label them as tests. Only genuine hosted evidence
  belongs in the final real-run proof bundle.
- Required checks: lint, formatting, strict typing, full tests, intentional-failure check,
  GitLab pipeline, clean-clone smoke test, public artifact access.

## Demo and video workstream

The working demo is the public GitLab workflow plus reproducible CLI/evidence report.
Record the real asynchronous run first; edit waiting periods out with honest captions.
Keep pipeline IDs, SHAs and session identifiers consistent between clips and report.

| Time | Screen | Evidence |
| --- | --- | --- |
| 0:00–0:15 | Problem and one-sentence value | Clear audience and recovery claim |
| 0:15–0:40 | Baseline, fault diff, red job | Actual URL/SHA and failing assertion |
| 0:40–1:25 | Duo session and proposed patch | Native platform execution; root cause |
| 1:25–1:45 | Human review and approval | Allowed-file diff; visible approval step |
| 1:45–2:15 | Successful rerun and CLI report | Expected SHA, same tests, actual green pipeline |
| 2:15–2:35 | Rejected false-green evidence and repo | Distinctive trust check and reproduction instructions |

Target 2:35 and keep below 3:00. Use English narration/captions, readable zoom, clean
browser profile, disabled notifications and licensed assets. Upload Public or Unlisted
to YouTube; check without account login. Keep an unedited capture privately for consistency
checks. Do not claim measured time savings from edited video duration.

## Lexsi: reserved plan after GitLab

**FaultLine-Tune hypothesis:** post-training improves recovery decisions for controlled tool
failures while preserving safe refusal/escalation on unauthorized actions. Stronger tool
syntax alone is insufficient; evaluate task completion and safety together.

No training implementation before GitLab submission. Planning now is safe; actual event
work starts within Lexsi's permitted build period in a separate repo. Track 3 plan:
AgentTune training/evaluation workflow, with AuditKIT integration if supported by its actual
interfaces. Choose an eligible Tiny Aya model after checking its model card, license,
tool-call format and GPU memory. AgentTune currently documents Python 3.12+ and an RL
training API; do not assume it offers the handoff's proposed SFT/QLoRA path without a spike.
[AgentTune documentation](https://agenttune.lexsi.ai/)

Proposed experiment sequence:

1. Nov 1–2: freeze environment/model revision and collect baseline on a tiny smoke suite;
   verify an actual optimizer step and saved adapter can reload on available GPU.
2. Nov 3–5: create deterministic sandbox tool environments: timeout, invalid arguments,
   permission denial, stale state and deceptive tool output. Define oracle outcomes,
   retry limits and escalation policy. Generate only authorized synthetic data.
3. Split by task template/fault family before trajectory generation; use separate seeds
   and deduplicate near-identical prompts. Lock held-out evaluation; never select checkpoints
   using test performance. Report interpolation and unseen-family results separately.
4. Nov 6–8: run small post-training pilot using a supported AgentTune algorithm; document
   training budget and failure modes. Expand only after before/after evaluation works.
5. Nov 9–11: compare same base and trained model with identical harness, tools, prompts,
   decoding policy, call/token limits and seeds. Include a prompt-only control and ablation
   if time permits. Record numerator/denominator and uncertainty, including regressions.
6. Nov 12–13: publish model/adapter revisions, datasets, logs, configs, evaluation results,
   model/data cards and HF article. Build a Space only if useful; record fallback video.
7. Submit by internal Nov 13 target; confirm Nov 14 timezone with organizers. If shortlisted,
   use Nov 16–21 for replication and stronger evidence; live demo Nov 22.

Primary metrics: completed tasks / all tasks; valid tool calls / all calls; unauthorized
action rate; unnecessary calls per task. Secondary latency/cost only from actual measured
runs on named hardware. Publish negative results; do not imply repaired CI code constitutes
a trained model. Keep GPU spend bounded with explicit owner budget before paid provisioning.

## Meta: conditional plan

Await acceptance and final rules before allocating implementation time or assuming code
reuse is permitted. Do not confuse “applied” with “accepted.” Recheck account notification
by Oct 26; GitLab remains first even if accepted.

If eligible, build **FaultLine Lab** in a separate repository after GitLab: a sandboxed
software-tool reliability benchmark with deterministic faults, one available Meta model
adapter, a fixed oracle and replay reports. Start with three tasks and a no-recovery
control. Add one recovery policy; compare same tasks/seeds/budgets. Require completed
work products rather than self-reported success. Keep this materially distinct from the
GitLab repair integration and from Lexsi post-training.

Oct 28–29: final-rule/model-access spike and minimal runner; Oct 30–Nov 1: controlled
experiments; Nov 2: report/demo; Nov 3: video and clean setup; Nov 4: early submission.
If that schedule conflicts with a viable Lexsi build, choose deliberately after GitLab;
do not promise three polished submissions simultaneously. Meta video format, license,
artifact fields and prior-code permissions remain pending final rules.

## Immediate dependencies

Owner input needed: GitLab onboarding/Duo status and provisioned project URL; personal
commit email before commits. Never share raw tokens in chat. The environment currently
has uv and Python 3.12 available, but no `glab`; browser UI and documented REST reads suffice
for P0. This turn does not create an external project, upload media or submit Devpost.
