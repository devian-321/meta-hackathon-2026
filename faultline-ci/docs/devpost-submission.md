# Devpost submission copy — October 27

This is copy-ready text for the current implemented prototype. Recheck the evidence
ledger before submitting. Native Duo execution, public access and the required video
URL are outstanding; this text does not establish eligibility by itself.

## Project name

FaultLine CI

## Tagline

Check the repair, not just the green pipeline.

## Path and autonomy

Path A: Start Fresh. Intended autonomy: Assisted. The native repair is designed to be
reviewed before acceptance. Human approval has not yet been demonstrated in a live run.

## Inspiration

A green pipeline is useful evidence, but it does not establish that a repair addressed
the original problem. A change can hide failing assertions or alter the checks themselves.
FaultLine CI explores how developers can independently check an AI-proposed CI repair.

## What it does

FaultLine CI combines a reproducible invoice-pricing regression with an independent
recovery verifier. The controlled bug adds a discount instead of subtracting it. A local
rehearsal runs real Git commits and pytest processes through four stages: a healthy
baseline, the injected fault, a scripted correction and a dishonest change that disables
the pricing assertions. The correction passes the repository guard; the dishonest change
is rejected even though its tests report green.

The GitLab adapter reads pipeline, job, test-report and repository evidence. Its outcome
checks require the expected repair commit, successful sample tests and preserved test
identities. With the repair guard enabled, it also checks ancestry, unchanged repository
objects outside the allowed correction and the exact pinned before/after pricing files.
Reports are available as HTML, JSON and Markdown.

## How we built it

The implementation uses Python 3.12, typed modules, HTTPX, pytest, Ruff, strict mypy and a
committed uv lockfile. GitLab CI separates quality checks, sample-application tests and
verifier tests. The repository includes native Duo execution setup and instructions that
limit the controlled repair to the pricing implementation.

The planned assisted workflow is: observe the failing GitLab test job, invoke native
Fix Pipeline with Duo, review its proposed correction, approve the repair, observe the
rerun and independently verify the real pipeline IDs and repair SHA. That live workflow
has not yet completed. GitLab currently requires account identity verification before
both hosted CI jobs and Duo Agent Platform can execute. Existing failed pipelines created
zero jobs and are not evidence of the pricing assertion failures.

## Challenges

Reliable evidence was the main engineering challenge: a passing result must not silently
lose tests, use an unexpected commit or accept modified verification code. The adapter
handles pagination, validates Git object content and fails closed when evidence is
incomplete. Reports publish into new directories so a failed write cannot overwrite an
earlier report. The local demo also isolates each mutation from the working checkout.

## Accomplishments

The application has 81 passing tests, with a further 16 workspace-setup tests. The fresh
local evidence bundle demonstrates eight passing sample tests, three expected failures
after the fault, eight passing tests after scripted restoration and a rejected false
green. The bundle includes JUnit reports, exact commit IDs and cloneable local history.
These are local results; the restoration is scripted and is not an AI-generated repair.

## What we learned

Recovery needs both outcome evidence and change-integrity evidence. A passing test count
alone cannot tell whether the original assertions still check the original behavior.
Native agent provenance and human approval also need their own evidence; neither should
be inferred from a successful test run.

## What's next

Complete the account prerequisite and demonstrate the native assisted recovery on real
GitLab pipelines. Then extend beyond the deliberately narrow pricing fixture with explicit
review policies for broader changes. General patch auditing, autonomous merging and
production deployment are outside the current implementation.

## Built with

Python, GitLab CI/CD, Git, pytest, HTTPX, uv, Ruff, mypy, JUnit XML, HTML.
GitLab Duo Agent Platform integration is configured but execution remains blocked.

## Links to enter

- Repository: https://gitlab.com/student-group4903843/fault-cli
- Controlled fault MR: https://gitlab.com/student-group4903843/fault-cli/-/merge_requests/1
- Local demo: `demo/evidence/local-rehearsal-2026-10-27/recovery.html` in the repository.
- Video: enter the actual uploaded YouTube URL; none is published yet.
- Deployment: not required for Path A; no Google Cloud bonus claimed.

Do not claim completed native Duo use, hosted recovery, human approval, public judge
access or a submission receipt until each has been observed. If native execution succeeds
before the deadline, replace the blocked-workflow paragraph with the actual session,
pipeline, approval and verifier links; keep the local rehearsal clearly distinguished.
