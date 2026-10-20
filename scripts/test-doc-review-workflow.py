"""Test the workflow's actual parameter extraction script (requires PyYAML).

Run with: python3 scripts/test-doc-review-workflow.py
"""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/doc_review.yml"


class DocReviewWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        cls.condition = workflow["jobs"]["prepare"]["if"]
        cls.step = next(
            step for step in workflow["jobs"]["prepare"]["steps"]
            if step.get("id") == "extract"
        )

    def run_comment(self, comment, expected, succeeds=True):
        with tempfile.TemporaryDirectory(prefix="doc-review-test-") as directory:
            output = Path(directory) / "github output"
            output.touch()
            marker = Path(directory) / "injected"
            comment = comment.replace("MARKER", str(marker))
            result = subprocess.run(
                ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", self.step["run"]],
                env={**os.environ, "COMMENT": comment, "GITHUB_OUTPUT": str(output)},
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0 if succeeds else 1, result.stderr)
            self.assertFalse(marker.exists(), "Comment executed a shell command")
            self.assertEqual(
                dict(line.split("=", 1) for line in output.read_text().splitlines()),
                expected,
            )
            self.assertNotIn("::warning::injected", result.stdout + result.stderr)

    def test_comment_is_passed_as_data(self):
        self.assertEqual(self.step["env"]["COMMENT"], "${{ github.event.comment.body }}")
        self.assertNotIn("${{", self.step["run"])

    def test_trigger_permissions(self):
        # Evaluate the workflow's condition for the supported event fields.
        expression = self.condition.replace("&&", " and ").replace("||", " or ")
        for field, variable in {
            "github.event_name": "event_name",
            "github.event.comment.body": "comment",
            "github.event.comment.user.login": "login",
            "github.event.comment.author_association": "association",
        }.items():
            expression = expression.replace(field, variable)

        allowed_logins = {"hfxsd", "likidu", "lilin90", "Oreoxmt", "qiancai"}
        allowed_associations = {"OWNER", "MEMBER", "COLLABORATOR"}
        for event_name in ["issue_comment", "workflow_dispatch", "push"]:
            for login in sorted(allowed_logins | {"outsider"}):
                for association in [
                    "OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR",
                    "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR", "MANNEQUIN", "NONE", "",
                ]:
                    for comment in ["/bot-review", "unrelated comment"]:
                        expected = event_name == "workflow_dispatch" or (
                            event_name == "issue_comment"
                            and login in allowed_logins
                            and association in allowed_associations
                            and "/bot-review" in comment
                        )
                        with self.subTest(event=event_name, login=login,
                                          association=association, comment=comment):
                            actual = eval(expression, {"__builtins__": {}}, {
                                "event_name": event_name, "login": login,
                                "association": association, "comment": comment,
                                "contains": lambda value, part: part in value,
                            })
                            self.assertEqual(actual, expected)

    def test_valid_commands(self):
        cases = [
            ("/bot-review", {"REVIEW_MODE": "latest"}),
            ("/bot-review \n", {"REVIEW_MODE": "latest"}),
            ("/bot-review: abc1234", {"REVIEW_MODE": "single_commit", "COMMIT_SHA": "abc1234"}),
            ("/bot-review:abc1234", {"REVIEW_MODE": "single_commit", "COMMIT_SHA": "abc1234"}),
            ("/bot-review: " + "a" * 40, {"REVIEW_MODE": "single_commit", "COMMIT_SHA": "a" * 40}),
            ("/bot-review:abc1234..def5678", {
                "REVIEW_MODE": "commit_range", "BASE_SHA": "abc1234", "HEAD_SHA": "def5678",
            }),
            ("/bot-review: abc1234 .. def5678 \n", {
                "REVIEW_MODE": "commit_range", "BASE_SHA": "abc1234", "HEAD_SHA": "def5678",
            }),
        ]
        for comment, expected in cases:
            with self.subTest(comment=comment):
                self.run_comment(comment, expected)

    def test_malicious_comments(self):
        payloads = [
            '"; touch MARKER; #',
            "$(touch MARKER)",
            "`touch MARKER`",
            '\"\n touch MARKER\n#',
            "\n::warning::injected",
            "\nREVIEW_MODE=latest",
        ]
        for command in ["/bot-review", "/bot-review: abc1234", "/bot-review:abc1234..def5678"]:
            for payload in payloads:
                with self.subTest(command=command, payload=payload):
                    self.run_comment(command + payload, {"REVIEW_MODE": "invalid"}, succeeds=False)

    def test_invalid_commands(self):
        for comment in [
            "", "quoted /bot-review: abc1234", "> /bot-review: abc1234",
            "/bot-review: abc123", "/bot-review: " + "a" * 41,
            "/bot-review: ghijklm", "/bot-review: abc1234junk",
            "/bot-review: abc1234..def5678junk", "/bot-review: abc1234..",
        ]:
            with self.subTest(comment=comment):
                self.run_comment(comment, {"REVIEW_MODE": "invalid"}, succeeds=False)


if __name__ == "__main__":
    unittest.main()
