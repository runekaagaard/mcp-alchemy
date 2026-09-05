FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install uv \
    && uv sync

# Common database drivers so the image works out of the box
RUN VIRTUAL_ENV=/app/.venv uv pip install psycopg2-binary pymysql pymssql oracledb

CMD ["uv", "run", "--directory", "/app", "-m", "mcp_alchemy.server"]
