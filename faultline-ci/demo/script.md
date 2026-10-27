# Demo capture script — target 2:35

Use this preferred sequence only after a genuine Duo repair and real red/green pipelines
exist. While account verification blocks both, use the explicitly local fallback below.

| Time | Capture | Narration intent |
| --- | --- | --- |
| 0:00–0:15 | Project and clean invoice tests | CI repairs need objective evidence |
| 0:15–0:40 | Fault diff, failed job and pipeline ID | A reproducible discount regression |
| 0:40–1:25 | Native Duo session, diagnosis, proposed repair | What Duo actually did |
| 1:25–1:45 | Diff review and human approval | The explicit approval boundary |
| 1:45–2:15 | Real green rerun and outcome report | Expected commit and preserved tests |
| 2:15–2:35 | Rejected false-green and repo instructions | Why independent checks matter |

Keep IDs/SHAs consistent across clips. Caption elapsed asynchronous waits honestly. Do not
present edited duration as measured recovery latency. Use readable zoom, English narration,
no secrets/notifications, and no unlicensed media. Publish on YouTube as Public or Unlisted;
check in a signed-out browser. Retain the original capture privately.

## Available now: local evidence walkthrough

The fallback demonstrates implemented behavior without claiming native execution. It does
not fulfill the required Duo demonstration by itself. Keep the label **Local rehearsal —
scripted repair; Duo not run** visible. Show the actual report rather than a fabricated
terminal session. The video should last about two minutes and use English narration.

1. Introduce the problem: a green pipeline can conceal a dishonest repair.
2. Open `demo/evidence/local-rehearsal-2026-10-27/recovery.html` and identify the local
   scope and observed timestamp. The report comes from real Git and pytest subprocesses.
3. Show the healthy eight-test baseline and three intended failures after injection.
   Explain the discount sign change in `sample_app/pricing.py`.
4. Show the scripted restoration: eight tests pass and the repository guard accepts it.
5. Show the disabled-assertion case: tests report green, but the guard rejects it because
   the tests changed and the original pricing defect remains.
6. Point to JUnit reports, exact local commit IDs and `demo.bundle` for inspection.
7. State the hosted blocker honestly: account verification is required before GitLab CI
   and Duo can execute. Show the proposed native sequence as future work, clearly labeled.

`build_video.py` produces a narrated MP4 and captions from the measured JSON evidence.
It presents evidence panels, not a recording of a live hosted agent session. Its image
rendering uses Pillow; macOS `say`, `ffmpeg` and `ffprobe` provide narration and encoding.
Keep generated video/audio out of source control and upload the reviewed MP4 manually.

For example, from the canonical application's root on macOS, with the optional media
dependencies installed in a separate local environment:

```sh
python demo/build_video.py --evidence demo/evidence/local-rehearsal-2026-10-27/recovery.json --output /NEW/LOCAL/OUTPUT/DIRECTORY
```

Use `demo/requirements-video.txt` for the renderer's Python dependency. Output includes
`faultline-local-walkthrough.mp4`, `captions.srt`, a transcript and a checksum manifest.
Review the video before uploading; it describes local evidence and the current blocker.
