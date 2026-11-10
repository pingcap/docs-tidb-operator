#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yaml"
RUN_CHECK = ROOT / "hack/run-doc-check.sh"


def test_workflow_passes_context_and_filenames_as_data() -> None:
    workflow = WORKFLOW.read_text()

    assert "permissions:\n  contents: read" in workflow
    assert "env:\n  BASE_REF: ${{ github.base_ref }}" in workflow
    assert workflow.count("${{ github.base_ref }}") == 1
    assert "$(git diff-tree" not in workflow
    assert workflow.count("./hack/run-doc-check.sh") == 5
    assert "python3 scripts/test-ci-workflow.py" in workflow


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def test_runner_preserves_untrusted_inputs() -> None:
    with tempfile.TemporaryDirectory(prefix="ci-file-handling-") as directory:
        root = Path(directory)
        run(["git", "init", "-q"], root)
        run(["git", "config", "user.email", "test@example.com"], root)
        run(["git", "config", "user.name", "CI test"], root)

        (root / "base.txt").write_text("base\n")
        run(["git", "add", "base.txt"], root)
        run(["git", "commit", "-qm", "base"], root)
        base_commit = run(["git", "rev-parse", "HEAD"], root).stdout.strip()

        base_ref = "main;touch${IFS}SHOULD_NOT_RUN;#"
        run(["git", "check-ref-format", "--branch", base_ref], root)
        run(
            ["git", "update-ref", f"refs/remotes/upstream/{base_ref}", base_commit],
            root,
        )

        changed_paths = [
            "normal.md",
            "space name.md",
            "line\nbreak.md",
            "$(touch SHOULD_NOT_RUN).md",
            "[draft]*?.md",
            "-leading.md",
        ]
        for path in changed_paths:
            (root / path).write_text(f"{path}\n")
        (root / "ignored.txt").write_text("not Markdown\n")
        run(["git", "add", "--", *changed_paths, "ignored.txt"], root)
        run(["git", "commit", "-qm", "add test files"], root)

        capture = root / "arguments.bin"
        checker = root / "check-file-encoding.py"
        checker.write_text(
            "import os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['CAPTURE']).write_bytes("
            "b'\\0'.join(os.fsencode(arg) for arg in sys.argv[1:]))\n"
        )

        environment = {
            **os.environ,
            "BASE_REF": base_ref,
            "CAPTURE": str(capture),
            "RUNNER_TEMP": directory,
        }
        subprocess.run(
            [
                "bash",
                str(RUN_CHECK),
                "check-file-encoding.py",
                "..",
                "*.md",
            ],
            cwd=root,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )

        arguments = [
            os.fsdecode(argument)
            for argument in capture.read_bytes().split(b"\0")
            if argument
        ]
        assert set(arguments) == {f"./{path}" for path in changed_paths}
        assert len(arguments) == len(changed_paths)
        assert not (root / "SHOULD_NOT_RUN").exists()


if __name__ == "__main__":
    test_workflow_passes_context_and_filenames_as_data()
    test_runner_preserves_untrusted_inputs()
    print("CI workflow tests passed")
