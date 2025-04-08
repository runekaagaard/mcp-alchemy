SHELL := /bin/bash
.SHELLFLAGS := -c

.PHONY: publish-test package-inspect-test package-run-test publish-prod

publish-test:
	rm -rf dist/*
	sed -i "s/version = \"[^\"]*\"/version = \"$(shell date +%Y.%m.%d.%H%M%S)\"/" pyproject.toml
	uv build
	uv publish --token "$$PYPI_TOKEN_TEST" --publish-url https://test.pypi.org/legacy/

publish-prod:
	rm -rf dist/*
	$(eval VERSION := $(shell date +%Y.%m.%d.%H%M%S))
	echo "$(VERSION)" > VERSION.txt
	sed -i "s/version = \"[^\"]*\"/version = \"$(VERSION)\"/" pyproject.toml
	uv build
	uv publish --token "$$PYPI_TOKEN_PROD"
	sed -i 's/mcp-alchemy==[0-9.]*"/mcp-alchemy==$(VERSION)"/g' README.md
	git commit -am "Publishing version $(VERSION) to pypi"

package-inspect-test:
	rm -rf /tmp/test-mcp-alchemy
	uv venv /tmp/test-mcp-alchemy --python 3.12
	source /tmp/test-mcp-alchemy/bin/activate && uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-alchemy
	tree /tmp/test-mcp-alchemy/lib/python3.12/site-packages/mcp_alchemy
	source /tmp/test-mcp-alchemy/bin/activate && which mcp-alchemy

package-inspect-prod:
	rm -rf /tmp/test-mcp-alchemy
	uv venv /tmp/test-mcp-alchemy --python 3.12
	source /tmp/test-mcp-alchemy/bin/activate && uv pip install mcp-alchemy
	tree /tmp/test-mcp-alchemy/lib/python3.12/site-packages/mcp_alchemy
	source /tmp/test-mcp-alchemy/bin/activate && which mcp-alchemy

package-run-test:
	uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ --from mcp-alchemy mcp-alchemy

package-run-prod:
	uvx --from mcp-alchemy mcp-alchemy
