SHELL := /bin/bash
.SHELLFLAGS := -ec

PROJECT := $(shell grep '^name = ' pyproject.toml | cut -d '"' -f2)
PACKAGE := $(shell echo $(PROJECT) | tr '-' '_')
VERSION := $(shell date +%Y.%m.%d.%H%M%S | sed 's/\.0\+/\./g')

version-bump:
	sed -i 's/"$(PROJECT)==[^"]*"/"$(PROJECT)==$(VERSION)"/g' README.md
	sed -i "s/version = \"[^\"]*\"/version = \"$(VERSION)\"/" pyproject.toml
	sed -i "s/VERSION = \"[^\"]*\"/VERSION = \"$(VERSION)\"/" $(PACKAGE)/server.py

version-bump-claude-desktop:
	sed -i "s/$(PROJECT)==[0-9.]*\"/$(PROJECT)==$(VERSION)\"/g" ~/.config/Claude/claude_desktop_config.json

publish-test:
	rm -rf dist/*
	$(MAKE) version-bump
	uv build
	uv publish --token "$$PYPI_TOKEN_TEST" --publish-url https://test.pypi.org/legacy/
	git checkout README.md pyproject.toml $(PACKAGE)/server.py

publish-prod:
	rm -rf dist/*
	$(MAKE) version-bump
	$(MAKE) version-bump-claude-desktop
	uv build
	uv lock
	uv publish --token "$$PYPI_TOKEN_PROD"
	git commit -am "Published version $(VERSION) to PyPI"
	git push

package-inspect-test:
	rm -rf /tmp/test-$(PROJECT)
	uv venv /tmp/test-$(PROJECT) --python 3.12
	source /tmp/test-$(PROJECT)/bin/activate && uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ $(PROJECT)
	tree /tmp/test-$(PROJECT)/lib/python3.12/site-packages/$(PACKAGE)
	source /tmp/test-$(PROJECT)/bin/activate && which $(PROJECT)

package-inspect-prod:
	rm -rf /tmp/test-$(PROJECT)
	uv venv /tmp/test-$(PROJECT) --python 3.12
	source /tmp/test-$(PROJECT)/bin/activate && uv pip install $(PROJECT)
	tree /tmp/test-$(PROJECT)/lib/python3.12/site-packages/$(PACKAGE)
	source /tmp/test-$(PROJECT)/bin/activate && which $(PROJECT)

package-run-test:
	uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ --from $(PROJECT) $(PROJECT)

package-run-prod:
	uvx --from $(PROJECT) $(PROJECT)

tests-run:
	DB_URL="sqlite:///tests/Chinook_Sqlite.sqlite" .venv/bin/python -m tests.test

debug-constants:
	@echo "PROJECT='$(PROJECT)'"
	@echo "PACKAGE='$(PACKAGE)'"
	@echo "VERSION='$(VERSION)'"
