"""Render an explicitly local evidence walkthrough; never simulate a hosted session.

Optional media tools: Pillow 11.3.0, macOS say, ffmpeg and ffprobe.
Run from the project root; use a new output directory outside the committed source.
"""

import argparse
import hashlib
import json
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_ROOT = Path("/System/Library/Fonts")
REGULAR = FONT_ROOT / "Supplemental/Arial.ttf"
BOLD = FONT_ROOT / "Supplemental/Arial Bold.ttf"
MONO = FONT_ROOT / "Menlo.ttc"


def run(*args: str) -> None:
    subprocess.run(args, check=True, capture_output=True, timeout=120)


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole, fraction = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{whole:02},{fraction:03}"


def panel(path: Path, number: int, title: str, lines: list[str], accent: str) -> None:
    image = Image.new("RGB", (1280, 720), "#101827")
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype(str(REGULAR), 28)
    small = ImageFont.truetype(str(REGULAR), 21)
    title_font = ImageFont.truetype(str(BOLD), 45)
    mono = ImageFont.truetype(str(MONO), 22)
    draw.rectangle((0, 0, 14, 720), fill=accent)
    draw.text((60, 36), "FAULTLINE CI", font=small, fill="#b7c3d7")
    draw.text((1120, 36), f"{number:02} / 07", font=small, fill="#b7c3d7")
    draw.text((60, 100), title, font=title_font, fill="white")
    draw.rounded_rectangle((60, 184, 1220, 568), radius=18, fill="#1b2940")
    y = 212
    for line in lines:
        font = mono if line.startswith(("commit ", "return ", "observed ", "SHA256 ")) else regular
        width = 78 if font is mono else 71
        for wrapped in textwrap.wrap(line, width=width) or [""]:
            draw.text((88, y), wrapped, font=font, fill="#ecf0f7")
            y += 35
        y += 9
    if y > 564:
        raise ValueError("Evidence panel text exceeds visible area")
    draw.text(
        (60, 608), "LOCAL REHEARSAL  /  SCRIPTED REPAIR  /  DUO NOT RUN", font=small, fill=accent
    )
    draw.text(
        (60, 651),
        "Real Git + pytest evidence. Hosted CI and Duo require account verification.",
        font=small,
        fill="#b7c3d7",
    )
    image.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    raw = evidence.read_bytes()
    report = json.loads(raw)
    if (report.get("source"), report.get("duo_provenance"), report.get("repair_method")) != (
        "local_subprocess",
        "not_run",
        "scripted_fixture_restoration",
    ):
        raise ValueError("This renderer only supports explicitly scripted local evidence")
    runs = report["local_runs"]
    if len(runs) != 4 or [(r["tests"], r["failed"]) for r in runs] != [
        (8, 0),
        (8, 3),
        (8, 0),
        (8, 0),
    ]:
        raise ValueError("Measured outcomes do not match this walkthrough")
    if not report["repair_verification"]["passed"] or report["tampered_verification"]["passed"]:
        raise ValueError("Guard evidence does not match this walkthrough")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    digest = hashlib.sha256(raw).hexdigest()
    scenes = [
        (
            "Check the repair, not just the green",
            [
                "A passing test run can conceal a dishonest repair.",
                "FaultLine CI independently checks outcomes and code changes.",
                "This walkthrough uses real local Git and pytest evidence.",
                "The repair is scripted. GitLab Duo has not run.",
            ],
            "A green pipeline does not always mean the original problem was fixed. "
            "FaultLine C I checks the repair as well as the result. This is a local evidence "
            "walkthrough with real Git and test runs. The repair is scripted; Duo has not run.",
        ),
        (
            "1. Establish a healthy baseline",
            [
                "Invoice totals use integer cents and a percentage discount.",
                "Measured sample tests: 8 passed / 0 failed / 0 skipped",
                "commit " + runs[0]["commit_sha"],
                "observed " + report["observed_at"],
            ],
            "First, establish a healthy baseline. The sample invoice calculator uses integer "
            "cents and percentage discounts. All eight sample tests pass. This exact local "
            "commit and the test results are preserved in the evidence bundle.",
        ),
        (
            "2. Inject the discount regression",
            [
                "The fault adds the discount instead of subtracting it.",
                "return subtotal * (100 + discount_percent) // 100",
                "Measured sample tests: 5 passed / 3 failed / 0 skipped",
                "commit " + runs[1]["commit_sha"],
            ],
            "Next, inject a one character regression. The discount is added instead of "
            "subtracted. Three pricing assertions now fail and five tests still pass. "
            "These are measured local results, not hosted GitLab pipeline results.",
        ),
        (
            "3. Accept the narrow correction",
            [
                "Scripted restoration of the pinned healthy implementation.",
                "return subtotal * (100 - discount_percent) // 100",
                "Measured sample tests: 8 passed / 0 failed / 0 skipped",
                "Repository guard: PASS — ancestry, scope and fixture checked",
                "commit " + runs[2]["commit_sha"],
            ],
            "A scripted restoration fixes the sign. All eight tests pass again. The independent "
            "guard accepts the correction after checking commit ancestry, allowed change "
            "scope and the pinned pricing implementation. This does not demonstrate an A I repair.",
        ),
        (
            "4. Reject a dishonest green",
            [
                "A separate attempt disables the pricing assertions.",
                "Measured sample tests: 8 passed / 0 failed / 0 skipped",
                "Repository guard: FAIL — tests changed; pricing fault remains",
                "commit " + runs[3]["commit_sha"],
                "Green tests alone do not establish a valid correction.",
            ],
            "Now the counterexample. A different attempt disables the pricing assertions. "
            "The tests report green, but the guard rejects the change: the tests were altered "
            "and the pricing fault remains. This is why checking only pipeline status "
            "is insufficient.",
        ),
        (
            "Inspect the underlying evidence",
            [
                "HTML, JSON and Markdown reports",
                "Four JUnit files and a cloneable demo.bundle",
                "Exact local commits and repository object checks",
                "JSON SHA256 prefix: " + digest[:32],
                "See demo/evidence/local-rehearsal-2026-10-27/",
            ],
            "The repository includes the full reports, four J Unit files and a cloneable Git "
            "bundle. Reviewers can inspect the exact commits and reproduce the command. "
            "The local history is separate from the hosted merge request.",
        ),
        (
            "Next: demonstrate native recovery",
            [
                "IMPLEMENTED: local rehearsal and independent verifier",
                "BLOCKED: GitLab CI and Duo require account verification",
                "PLANNED: failing job → Duo proposal → human review",
                "Then: real green rerun → independent API verification",
                "No completed hosted recovery or human approval claimed.",
            ],
            "The GitLab adapter and native repair instructions are implemented. Account "
            "verification currently blocks both hosted jobs and Duo. The next step is a real "
            "Duo proposal, human review and a green rerun checked through the GitLab A P I. "
            "That live recovery remains unverified.",
        ),
    ]
    captions = []
    elapsed = 0.0
    transcript = []
    for index, (title, lines, narration) in enumerate(scenes, 1):
        prefix = output / f"scene-{index:02}"
        image = prefix.with_suffix(".png")
        audio = prefix.with_suffix(".aiff")
        panel(image, index, title, lines, "#ffb47c" if index in (3, 5, 7) else "#7be3cf")
        text = prefix.with_suffix(".txt")
        text.write_text(narration + "\n")
        run("say", "-v", "Samantha", "-r", "165", "-f", str(text), "-o", str(audio))
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(audio),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        duration = float(probe.stdout) + 0.5
        run(
            "ffmpeg",
            "-v",
            "error",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(image),
            "-i",
            str(audio),
            "-af",
            "apad=pad_dur=0.5",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(prefix.with_suffix(".mp4")),
        )
        sentences = narration.split(". ")
        for sentence in sentences:
            part = duration * len(sentence) / sum(len(item) for item in sentences)
            captions.append(
                f"{len(captions) + 1}\n{timestamp(elapsed)} --> {timestamp(elapsed + part)}\n"
                f"{sentence}\n"
            )
            elapsed += part
        transcript.append(f"{index}. {title}\n{narration}\n")
    if elapsed >= 180:
        raise ValueError("Walkthrough exceeds the three-minute video limit")
    listing = output / "segments.txt"
    listing.write_text("".join(f"file 'scene-{index:02}.mp4'\n" for index in range(1, 8)))
    run(
        "ffmpeg",
        "-v",
        "error",
        "-f",
        "concat",
        "-safe",
        "1",
        "-i",
        str(listing),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(output / "faultline-local-walkthrough.mp4"),
    )
    (output / "captions.srt").write_text("\n".join(captions))
    (output / "transcript.txt").write_text("\n".join(transcript))
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "source": "local_evidence_panels",
                "duo_provenance": "not_run",
                "repair_method": report["repair_method"],
                "evidence_sha256": digest,
                "estimated_seconds": round(elapsed, 3),
                "narration": "macOS Samantha synthetic voice",
                "video_sha256": hashlib.sha256(
                    (output / "faultline-local-walkthrough.mp4").read_bytes()
                ).hexdigest(),
            },
            indent=2,
        )
        + "\n"
    )
    print(
        f"Rendered {elapsed:.1f}s local walkthrough: {output / 'faultline-local-walkthrough.mp4'}"
    )


if __name__ == "__main__":
    main()
