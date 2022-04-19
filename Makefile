SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c 'echo [$@]: + $$0 && eval "$$0" 2>&1 | sed -e "s/^/[$@]: /;"'

BASE_REF := master

all: check-file-encoding check-git-conflicts markdownlint verify-internal-links verify-internal-link-anchors check-control-characters check-unclosed-tags check-manual-line-breaks

check-file-encoding:
	wget https://raw.githubusercontent.com/pingcap/docs/master/scripts/check-file-encoding.py
	python3 check-file-encoding.py $$(git diff-tree --name-only --no-commit-id -r upstream/$(BASE_REF)..HEAD -- '*.md' ':(exclude).github/*')

check-git-conflicts:
	wget https://raw.githubusercontent.com/pingcap/docs/master/scripts/check-conflicts.py
	python3 check-conflicts.py $$(git diff-tree --name-only --no-commit-id -r upstream/$(BASE_REF)..HEAD -- '*.md' '*.yml' '*.yaml')

markdownlint:
	./hack/markdownlint.sh

verify-internal-links:
	./hack/verify-links.sh

verify-internal-link-anchors:
	./hack/verify-link-anchors.sh

check-control-characters:
	wget https://raw.githubusercontent.com/pingcap/docs/master/scripts/check-control-char.py
	python3 check-control-char.py $$(git diff-tree --name-only --no-commit-id -r upstream/$(BASE_REF)..HEAD -- '*.md' ':(exclude).github/*')

check-unclosed-tags:
	wget https://raw.githubusercontent.com/pingcap/docs/master/scripts/check-tags.py
	python3 check-tags.py $$(git diff-tree --name-only --no-commit-id -r upstream/$(BASE_REF)...HEAD -- 'zh/' 'en/' '.md' ':(exclude).github/*')

check-manual-line-breaks:
	wget https://raw.githubusercontent.com/pingcap/docs/master/scripts/check-manual-line-breaks.py
	python3 check-manual-line-breaks.py $$(git diff-tree --name-only --no-commit-id -r upstream/$(BASE_REF)..HEAD -- '*.md' ':(exclude).github/*')
