# MCP Alchemy

**Status: Works great and is in daily use without any known bugs.**

**Status2: I just added the package to PYPI and updated the usage instructions. Please report any issues :)** 

Let Claude be your database expert! MCP Alchemy connects Claude Desktop directly to your databases, allowing it to:

- Help you explore and understand your database structure
- Assist in writing and validating SQL queries
- Displays relationships between tables
- Analyze large datasets and create reports
- Claude Desktop Can analyse and create artifacts for very large datasets using [claude-local-files](https://github.com/runekaagaard/claude-local-files).

Works with PostgreSQL, MySQL, MariaDB, SQLite, Oracle, MS SQL Server and a host of other [SQLAlchemy-compatible](https://docs.sqlalchemy.org/en/20/dialects/) databases.

![MCP Alchemy in action](screenshot.png)

## Installation

Ensure you have uv installed:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`. You need to add the appropriate database driver in the ``--with`` parameter.

### SQLite (built into Python)
```json
{
  "mcpServers": {
    "my_sqlite_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.04.08.212652", "mcp-alchemy"],
      "env": {
        "DB_URL": "sqlite:///path/to/database.db"
      }
    }
  }
}
```

### PostgreSQL
```json
{
  "mcpServers": {
    "my_postgres_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.04.08.212652", "--with", "psycopg2-binary", "mcp-alchemy"],
      "env": {
        "DB_URL": "postgresql://user:password@localhost/dbname"
      }
    }
  }
}
```

### MySQL/MariaDB
```json
{
  "mcpServers": {
    "my_mysql_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.04.08.212652", "--with", "pymysql", "mcp-alchemy"],
      "env": {
        "DB_URL": "mysql+pymysql://user:password@localhost/dbname"
      }
    }
  }
}
```

### Microsoft SQL Server
```json
{
  "mcpServers": {
    "my_mssql_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.04.08.212652", "--with", "pymssql", "mcp-alchemy"],
      "env": {
        "DB_URL": "mssql+pymssql://user:password@localhost/dbname"
      }
    }
  }
}
```

### Oracle
```json
{
  "mcpServers": {
    "my_oracle_db": {
      "command": "uvx",
      "args": ["--from", "mcp-alchemy==2025.04.08.212652", "--with", "cx_oracle", "mcp-alchemy"],
      "env": {
        "DB_URL": "oracle+cx_oracle://user:password@localhost/dbname"
      }
    }
  }
}
```

Environment Variables:

- `DB_URL`: SQLAlchemy [database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) (required)
- `CLAUDE_LOCAL_FILES_PATH`: Directory for full result sets (optional)
- `EXECUTE_QUERY_MAX_CHARS`: Maximum output length (optional, default 4000)

## API

### Tools

- **all_table_names**
  - Return all table names in the database
  - No input required
  - Returns comma-separated list of tables
  ```
  users, orders, products, categories
  ```

- **filter_table_names**
  - Find tables matching a substring
  - Input: `q` (string)
  - Returns matching table names
  ```
  Input: "user"
  Returns: "users, user_roles, user_permissions"
  ```

- **schema_definitions**
  - Get detailed schema for specified tables
  - Input: `table_names` (string[])
  - Returns table definitions including:
    - Column names and types
    - Primary keys
    - Foreign key relationships
    - Nullable flags
  ```
  users:
      id: INTEGER, primary key, autoincrement
      email: VARCHAR(255), nullable
      created_at: DATETIME
      
      Relationships:
        id -> orders.user_id
  ```

- **execute_query**
  - Execute SQL query with vertical output format
  - Inputs:
    - `query` (string): SQL query
    - `params` (object, optional): Query parameters
  - Returns results in clean vertical format:
  ```
  1. row
  id: 123
  name: John Doe
  created_at: 2024-03-15T14:30:00
  email: NULL

  Result: 1 rows
  ```
  - Features:
    - Smart truncation of large results
    - Full result set access via [claude-local-files](https://github.com/runekaagaard/claude-local-files) integration
    - Clean NULL value display
    - ISO formatted dates
    - Clear row separation

## Claude Local Files

When [claude-local-files](https://github.com/runekaagaard/claude-local-files) is configured:

- Access complete result sets beyond Claude's context window
- Generate detailed reports and visualizations
- Perform deep analysis on large datasets
- Export results for further processing

The integration automatically activates when `CLAUDE_LOCAL_FILES_PATH` is set.

## Contributing

Contributions are warmly welcomed! Whether it's bug reports, feature requests, documentation improvements, or code contributions - all input is valuable. Feel free to:

- Open an issue to report bugs or suggest features
- Submit pull requests with improvements
- Enhance documentation or share your usage examples
- Ask questions and share your experiences

The goal is to make database interaction with Claude even better, and your insights and contributions help achieve that.

## License

Mozilla Public License Version 2.0 
