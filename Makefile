SHELL := /bin/bash
.SHELLFLAGS := -c

.PHONY: publish-test package-inspect-test package-run-test

publish-test:
	rm -rf dist/*
	sed -i "s/version = \"[^\"]*\"/version = \"$(shell date +%Y.%m.%d.%H%M%S)\"/" pyproject.toml
	uv build
	uv publish --token "$$TEST_PYPI_TOKEN" --publish-url https://test.pypi.org/legacy/

package-inspect-test:
	rm -rf /tmp/test-mcp-alchemy
	uv venv /tmp/test-mcp-alchemy --python 3.12
	source /tmp/test-mcp-alchemy/bin/activate && uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-alchemy
	tree /tmp/test-mcp-alchemy/lib/python3.12/site-packages/mcp_alchemy
	source /tmp/test-mcp-alchemy/bin/activate && which mcp-alchemy

package-run-test:
	uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ --from mcp-alchemy mcp-alchemy
