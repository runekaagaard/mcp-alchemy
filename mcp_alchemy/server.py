import os, json, hashlib
from typing import Optional
from datetime import datetime, date

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.utilities.logging import get_logger

from sqlalchemy import create_engine, inspect, text

### Helpers ###

def tests_set_global(k, v):
    globals()[k] = v

### Database ###

def get_engine(readonly=True):
    connection_string = os.environ['DB_URL']
    return create_engine(connection_string, isolation_level='AUTOCOMMIT', execution_options={'readonly': readonly})

def get_db_info():
    engine = get_engine(readonly=True)
    with engine.connect():
        url = engine.url
        result = [
            f"Connected to {engine.dialect.name}",
            f"version {'.'.join(str(x) for x in engine.dialect.server_version_info)}",
            f"database {url.database}",
        ]

        if url.host:
            result.append(f"on {url.host}")

        if url.username:
            result.append(f"as user {url.username}")

        return " ".join(result) + "."

### Constants ###

VERSION = "2025.4.23.194321"
DB_INFO = get_db_info()
EXECUTE_QUERY_MAX_CHARS = int(os.environ.get('EXECUTE_QUERY_MAX_CHARS', 4000))
CLAUDE_LOCAL_FILES_PATH = os.environ.get('CLAUDE_LOCAL_FILES_PATH')

### MCP ###

mcp = FastMCP("MCP Alchemy")
get_logger(__name__).info(f"Starting MCP Alchemy version {VERSION}")

@mcp.tool(description=f"Return all table names in the database separated by comma. {DB_INFO}")
def all_table_names() -> str:
    engine = get_engine()
    inspector = inspect(engine)
    return ", ".join(inspector.get_table_names())

@mcp.tool(
    description=f"Return all table names in the database containing the substring 'q' separated by comma. {DB_INFO}"
)
def filter_table_names(q: str) -> str:
    engine = get_engine()
    inspector = inspect(engine)
    return ", ".join(x for x in inspector.get_table_names() if q in x)

@mcp.tool(description=f"Returns schema and relation information for the given tables. {DB_INFO}")
def schema_definitions(table_names: list[str]) -> str:
    def format(inspector, table_name):
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        primary_keys = set(inspector.get_pk_constraint(table_name)["constrained_columns"])
        result = [f"{table_name}:"]

        # Process columns
        show_key_only = {"nullable", "autoincrement"}
        for column in columns:
            if "comment" in column:
                del column["comment"]
            name = column.pop("name")
            column_parts = (["primary key"] if name in primary_keys else []) + [str(
                column.pop("type"))] + [k if k in show_key_only else f"{k}={v}" for k, v in column.items() if v]
            result.append(f"    {name}: " + ", ".join(column_parts))

        # Process relationships
        if foreign_keys:
            result.extend(["", "    Relationships:"])
            for fk in foreign_keys:
                constrained_columns = ", ".join(fk['constrained_columns'])
                referred_table = fk['referred_table']
                referred_columns = ", ".join(fk['referred_columns'])
                result.append(f"      {constrained_columns} -> {referred_table}.{referred_columns}")

        return "\n".join(result)

    engine = get_engine()
    inspector = inspect(engine)
    return "\n".join(format(inspector, table_name) for table_name in table_names)

def execute_query_description():
    parts = [
        f"Execute a SQL query and return results in a readable format. Results will be truncated after {EXECUTE_QUERY_MAX_CHARS} characters."
    ]
    if CLAUDE_LOCAL_FILES_PATH:
        parts.append("Claude Desktop may fetch the full result set via an url for analysis and artifacts.")
    parts.append(
        "IMPORTANT: Always use the params parameter for query parameter substitution (e.g. 'WHERE id = :id' with "
        "params={'id': 123}) to prevent SQL injection. Direct string concatenation is a serious security risk.")
    parts.append(DB_INFO)
    return " ".join(parts)

@mcp.tool(description=execute_query_description())
def execute_query(query: str, params: dict = {}) -> str:
    def format_value(val):
        """Format a value for display, handling None and datetime types"""
        if val is None:
            return "NULL"
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        return str(val)

    def format_result(cursor_result):
        """Format rows in a clean vertical format"""
        result, full_results = [], []
        size, i, did_truncate = 0, 0, False

        i = 0
        while row := cursor_result.fetchone():
            i += 1
            if CLAUDE_LOCAL_FILES_PATH:
                full_results.append(row)
            if did_truncate:
                continue

            sub_result = []
            sub_result.append(f"{i}. row")
            for col, val in zip(cursor_result.keys(), row):
                sub_result.append(f"{col}: {format_value(val)}")

            sub_result.append("")

            size += sum(len(x) + 1 for x in sub_result)  # +1 is for line endings

            if size > EXECUTE_QUERY_MAX_CHARS:
                did_truncate = True
                if not CLAUDE_LOCAL_FILES_PATH:
                    break
            else:
                result.extend(sub_result)

        if i == 0:
            return ["No rows returned"], full_results
        elif did_truncate:
            if CLAUDE_LOCAL_FILES_PATH:
                result.append(f"Result: {i} rows (output truncated)")
            else:
                result.append(f"Result: showing first {i-1} rows (output truncated)")
            return result, full_results
        else:
            result.append(f"Result: {i} rows")
            return result, full_results

    def save_full_results(full_results):
        """Save complete result set for Claude if configured"""
        if not CLAUDE_LOCAL_FILES_PATH:
            return None

        def serialize_row(row):
            return [format_value(val) for val in row]

        data = [serialize_row(row) for row in full_results]
        file_hash = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        file_name = f"{file_hash}.json"

        with open(os.path.join(CLAUDE_LOCAL_FILES_PATH, file_name), 'w') as f:
            json.dump(data, f)

        return (
            f"Full result set url: https://cdn.jsdelivr.net/pyodide/claude-local-files/{file_name}"
            " (format: [[row1_value1, row1_value2, ...], [row2_value1, row2_value2, ...], ...]])"
            " (ALWAYS prefer fetching this url in artifacts instead of hardcoding the values if at all possible)")

    try:
        engine = get_engine(readonly=False)
        with engine.connect() as connection:
            cursor_result = connection.execute(text(query), params)

            if not cursor_result.returns_rows:
                return f"Success: {cursor_result.rowcount} rows affected"

            output, full_results = format_result(cursor_result)

            if full_results_message := save_full_results(full_results):
                output.append(full_results_message)

            return "\n".join(output)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
