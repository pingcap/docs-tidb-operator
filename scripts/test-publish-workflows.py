"""Check publishing boundaries locally without accessing secrets or deploying."""

from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "pingcap/docs-tidb-operator"
RELEASES = {f"release-1.{minor}" for minor in range(7)} | {"release-2.0"}


def load(name):
    # BaseLoader preserves the YAML key "on" as a string.
    return yaml.load(
        (ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader
    )


def allowed(expression, **context):
    # Evaluate the limited boolean grammar used by these job conditions.
    expression = re.sub(
        r"github\.(repository|event_name|actor|triggering_actor)\b",
        lambda match: repr(context[match[1]]), expression,
    )
    expression = expression.replace("&&", " and ").replace("||", " or ")
    return eval(" ".join(expression.split()), {"__builtins__": {}}, {})


class PublishWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dispatch = load("dispatch.yml")
        cls.media = load("media.yml")

    def test_exact_push_branches(self):
        for workflow, extra in [(self.dispatch, set()), (self.media, {"release-1.x"})]:
            with self.subTest(workflow=workflow["name"]):
                branches = workflow["on"]["push"]["branches"]
                self.assertEqual(set(branches), RELEASES | {"main"} | extra)
                self.assertNotIn("release-zzz", branches)

    def test_all_credential_consumers_use_environments(self):
        expected = {
            "dispatch.yml": {"trigger": "docs-publish"},
            "media.yml": {"upload": "production-media", "cdn-refresh": "production-media"},
        }
        for filename, jobs in expected.items():
            workflow = load(filename)
            for name, job in workflow["jobs"].items():
                if "secrets." in str(job):
                    self.assertEqual(job["environment"], jobs[name])
            for name, environment in jobs.items():
                self.assertEqual(workflow["jobs"][name]["environment"], environment)
        self.assertEqual(self.media["jobs"]["cdn-refresh"]["needs"], "upload")

    def test_minimal_token_permissions(self):
        self.assertEqual(self.dispatch["permissions"], {})
        self.assertEqual(self.media["permissions"], {"contents": "read"})

    def test_manual_dispatch_and_rerun_actors(self):
        condition = self.media["jobs"]["upload"]["if"]
        for actor in ["lilin90", "qiancai", "other-writer"]:
            for triggering_actor in ["lilin90", "qiancai", "other-writer"]:
                with self.subTest(actor=actor, triggering_actor=triggering_actor):
                    self.assertEqual(
                        allowed(condition, repository=REPOSITORY,
                                event_name="workflow_dispatch", actor=actor,
                                triggering_actor=triggering_actor),
                        actor != "other-writer" and triggering_actor != "other-writer",
                    )

    def test_pushes_and_forks(self):
        for repository in [REPOSITORY, "other/docs-tidb-operator"]:
            context = dict(repository=repository, event_name="push",
                           actor="merge-bot", triggering_actor="merge-bot")
            self.assertEqual(
                allowed(self.dispatch["jobs"]["trigger"]["if"], **context),
                repository == REPOSITORY,
            )
            self.assertEqual(
                allowed(self.media["jobs"]["upload"]["if"], **context),
                repository == REPOSITORY,
            )
        self.assertFalse(allowed(
            self.media["jobs"]["upload"]["if"], repository=REPOSITORY,
            event_name="pull_request", actor="qiancai", triggering_actor="qiancai",
        ))


if __name__ == "__main__":
    unittest.main()
