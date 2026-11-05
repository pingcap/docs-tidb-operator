# Publish workflow environment setup

Complete this setup in `pingcap/docs-tidb-operator` before merging the workflow
changes. Merely naming an environment in YAML can create an unprotected
environment. Branch filters, actor checks, CODEOWNERS, and `permissions` do not
prevent a repository writer from creating another workflow that reads
repository-level secrets. `permissions` only limits `GITHUB_TOKEN`.

## Required administrator setup

Create the following environments under Settings > Environments:

| Environment | Environment secrets | Allowed deployment branches |
| --- | --- | --- |
| `docs-publish` | `DOCS_STAGING` | `main`, `release-1.0`, `release-1.1`, `release-1.2`, `release-1.3`, `release-1.4`, `release-1.5`, `release-1.6`, `release-2.0` |
| `production-media` | `TENCENTCLOUD_BUCKET_ID`, `TENCENTCLOUD_SECRET_ID`, `TENCENTCLOUD_SECRET_KEY` | Same branches as `docs-publish`, plus `release-1.x` |

For each environment:

1. Require review by the trusted publishing maintainers (`lilin90` and `qiancai`).
   Enable prevention of self-review and disable administrator bypass. GitHub
   requires approval from one of the listed reviewers, not both. Both media jobs
   reference the environment, so CDN refresh is gated as well as upload.
2. Select **Selected branches and tags**. Add each branch above as an exact
   **branch** rule. Do not add tag rules or a `release-*` wildcard, and do not use
   **Protected branches only**: new branches could match broader branch protection
   patterns. Keep the existing branch push restrictions in place.
3. Store the listed secrets in that environment. Remove their repository-level
   copies after checking all consumers across release branches. Also remove any
   organization-secret grants that expose the same credentials to this repository.
   Secret values cannot be retrieved through the GitHub API; obtain them from the
   credential owner or replace them. Rotate credentials if exposure is suspected.
4. Update these workflows on existing release branches to use the environments
   before removing the repository secrets. Old workflow revisions cannot access
   environment secrets without declaring the environment; re-running an older
   workflow may fail after migration. Coordinate the cutover to avoid publishing
   failures. Do not restore repository-level copies as a workaround.

Review any other consumers before moving a shared credential. Required reviewers
must inspect the workflow revision and content being deployed before approving:
an environment is not bound to a particular workflow filename. For a new release,
review and protect its branch, then update both the workflow allowlist and the
environment's exact branch rules.

Also add an active branch ruleset for `release-*` restricting branch creation to
the trusted maintainers through a narrowly scoped bypass list. Existing classic
rules cover `release-1.*` and `release-2.0`, not arbitrary new release names.
This is defense in depth; it does not replace secret migration because writers
could add a secret-reading workflow on another branch.

## Verification

- Run `actionlint .github/workflows/dispatch.yml .github/workflows/media.yml`,
  `python3 scripts/test-publish-workflows.py`, and
  `python3 scripts/test-dispatch-workflow.py` locally. These checks do not publish.
- Inspect environment protection and deployment branch rules through GitHub's
  settings or API, and confirm the publishing credential names are absent from
  repository secrets and applicable organization secrets.
- Use a separate dummy environment and dummy secrets to test a disallowed branch,
  a tag matching an allowed branch name, required approval, and self-review
  prevention. Do not test credential access by printing real secrets or running
  production uploads/CDN purges.
- After cutover, observe the next authorized production run: jobs must wait for
  environment approval before accessing credentials. A manual media dispatch by
  anyone outside the actor allowlist must skip upload and CDN refresh; trusted
  dispatches and re-runs still require environment approval and an allowed branch.

Until environment protections and secret migration are complete, the repository
writer credential-exfiltration risk remains. Changing triggers alone does not
close that risk.
