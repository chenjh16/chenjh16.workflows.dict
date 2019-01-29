.PHONY: default install

default:
	find . -type f \( -name '*.pyc' -or -name '.DS_Store' \) -exec rm -rf '{}' \; && \
	zip -r dict.alfredworkflow . -x Makefile -x '*.md' -x '.git*' -x '*.log' \
	-x 'README.md' -x 'playground.py' -x 'saveword.py' -x 'old_*'

install:default
	open dict.alfredworkflow
