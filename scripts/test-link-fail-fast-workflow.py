#!/usr/bin/env python3

import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/link-fail-fast.yaml"
CHECK_LINKS = ROOT / "hack/check-links.sh"


def test_workflow_uses_array_safe_path_handling() -> None:
    workflow = WORKFLOW.read_text()

    discovery = """\
          changed_list="$RUNNER_TEMP/changed-files.bin"
          if ! git diff-tree --name-only --diff-filter 'AMT' -z -r HEAD^1 HEAD -- \\
            "zh/*.md" "en/*.md" > "$changed_list"; then
            echo "Failed to discover changed Markdown files." >&2
            exit 1
          fi
          mapfile -d '' -t changed_files < "$changed_list"
"""
    assert discovery in workflow

    required = (
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "2cb75e6bcaf97f049d4e0260433938a77c60d39bd347d704502ae96c1e6f481c",
        'LYCHEE_BIN="$RUNNER_TEMP/lychee" ./hack/check-links.sh "${changed_files[@]}"',
    )
    for text in required:
        assert text in workflow, f"workflow is missing: {text}"

    forbidden = ("lycheeverse/lychee-action", "$GITHUB_OUTPUT")
    for text in forbidden:
        assert text not in workflow, f"workflow must not contain: {text}"


def test_check_script_escapes_glob_metacharacters() -> None:
    paths = (
        "zh/normal.md",
        "en/space name.md",
        "en/quote'file.md",
        "en/$(touch SHOULD_NOT_RUN).md",
        "en/[draft]*?.md",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        mock_lychee = temp / "lychee"
        mock_lychee.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "with open(os.environ['ARGS_FILE'], 'wb') as output:\n"
            "    for arg in sys.argv[1:]:\n"
            "        output.write(os.fsencode(arg) + b'\\0')\n"
        )
        os.chmod(mock_lychee, 0o755)

        args_file = temp / "args"
        environment = os.environ.copy()
        environment["ARGS_FILE"] = str(args_file)
        environment["LYCHEE_BIN"] = str(mock_lychee)
        subprocess.run(
            ["bash", str(CHECK_LINKS), *paths],
            cwd=temp,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

        arguments = [
            os.fsdecode(argument)
            for argument in args_file.read_bytes().split(b"\0")
            if argument
        ]
        separator = arguments.index("--")
        assert arguments[:separator] == [
            "--format",
            "markdown",
            "-E",
            "--exclude-mail",
            "-i",
            "-n",
            "-t",
            "45",
        ]
        assert arguments[separator + 1 :] == [
            "zh/normal.md",
            "en/space name.md",
            "en/quote'file.md",
            "en/$(touch SHOULD_NOT_RUN).md",
            "en/[[]draft[]][*][?].md",
        ]
        assert not (temp / "SHOULD_NOT_RUN").exists()


if __name__ == "__main__":
    test_workflow_uses_array_safe_path_handling()
    test_check_script_escapes_glob_metacharacters()
    print("link fail-fast workflow tests passed")
