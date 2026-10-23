"""Test the actual dispatch script without network access (requires PyYAML and jq).

Run with: python3 scripts/test-dispatch-workflow.py
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/dispatch.yml"


class DispatchWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        cls.step = next(
            step for step in workflow["jobs"]["trigger"]["steps"]
            if step["name"] == "trigger docs-staging workflow"
        )

    def test_context_and_secret_are_passed_as_data(self):
        self.assertEqual(self.step["env"], {
            "DOCS_STAGING": "${{ secrets.DOCS_STAGING }}",
            "REPOSITORY": "${{ github.repository }}",
            "BRANCH": "${{ github.ref_name }}",
        })
        self.assertNotIn("${{", self.step["run"])

    def run_dispatch(self, branch, repository="pingcap/docs-tidb-operator",
                     token="dummy-dispatch-token"):
        with tempfile.TemporaryDirectory(prefix="dispatch-test-") as directory:
            root = Path(directory)
            marker = root / "injected"
            branch = branch.replace("MARKER", str(marker))
            repository = repository.replace("MARKER", str(marker))
            token = token.replace("MARKER", str(marker))
            subprocess.run(
                ["git", "check-ref-format", "--branch", branch],
                check=True, capture_output=True, text=True,
            )
            capture = root / "curl-args.json"
            # Capture curl arguments locally; never make an HTTP request.
            curl = root / "curl"
            curl.write_text(
                f"#!{sys.executable}\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                "Path(os.environ['CURL_CAPTURE']).write_text(json.dumps(sys.argv[1:]))\n"
            )
            curl.chmod(0o755)
            result = subprocess.run(
                ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", self.step["run"]],
                env={
                    **os.environ,
                    "PATH": directory + os.pathsep + os.environ["PATH"],
                    "CURL_CAPTURE": str(capture),
                    "BRANCH": branch,
                    "REPOSITORY": repository,
                    "DOCS_STAGING": token,
                },
                cwd=directory, capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists(), "Input executed a shell command")
            self.assertNotIn(token, result.stdout + result.stderr)
            args = json.loads(capture.read_text())
            payload = json.loads(args[args.index("-d") + 1])
            self.assertEqual(payload, {
                "ref": "main",
                "inputs": {"full": "false", "repo": repository, "branch": branch},
            })
            self.assertEqual(args, [
                "-X", "POST",
                "-H", "Accept: application/vnd.github+json",
                "-H", f"Authorization: token {token}",
                "https://api.github.com/repos/pingcap/docs-staging/actions/workflows/update.yml/dispatches",
                "-d", args[args.index("-d") + 1],
            ])

    def test_normal_branches(self):
        for branch in ["main", "release-2.0"]:
            with self.subTest(branch=branch):
                self.run_dispatch(branch)

    def test_malicious_valid_branch_names(self):
        for branch in [
            "release-x'$(touch${IFS}MARKER)'",
            "release-x';touch${IFS}MARKER;#",
            'release-x"quoted',
            "release-$(touch${IFS}MARKER)",
            "release-`touch${IFS}MARKER`",
        ]:
            with self.subTest(branch=branch):
                self.run_dispatch(branch)

    def test_repository_and_token_remain_literal(self):
        self.run_dispatch(
            "main",
            repository='owner/repo"$(touch${IFS}MARKER)',
            token='dummy"$(touch${IFS}MARKER)`touch${IFS}MARKER`',
        )


if __name__ == "__main__":
    unittest.main()
