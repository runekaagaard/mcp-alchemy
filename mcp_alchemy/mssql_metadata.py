from sqlalchemy import text

def get_table_properties(connection, table_name, schema_name='dbo'):
    """Fetches extended properties for BOTH the table and its columns."""
    sql = text("""
        SELECT 
            CASE WHEN col.name IS NULL THEN 'TABLE_DESCRIPTION' ELSE col.name END AS column_name, 
            ep.value AS description
        FROM sys.extended_properties AS ep
        JOIN sys.objects AS obj ON ep.major_id = obj.object_id
        JOIN sys.schemas AS s ON obj.schema_id = s.schema_id
        -- Left join columns so we don't lose the Table-level property
        LEFT JOIN sys.columns AS col ON ep.major_id = col.object_id AND ep.minor_id = col.column_id
        WHERE obj.name = :table_name
          AND s.name = :schema_name
          AND ep.name = 'MS_Description'
    """)
    result = connection.execute(sql, {"table_name": table_name, "schema_name": schema_name})
    return {row.column_name: row.description for row in result}


def get_documented_procedures(connection):
    """Fetches only stored procedures that have an extended property description."""
    sql = text("""
               SELECT s.name + '.' + p.name AS full_name,
                      ep.value              AS description,
                      par.name              AS param_name,
                      typ.name              AS param_type
               FROM sys.procedures p
                        JOIN sys.schemas s ON p.schema_id = s.schema_id
                        JOIN sys.extended_properties ep ON p.object_id = ep.major_id AND ep.name = 'MS_Description'
                        LEFT JOIN sys.parameters par ON p.object_id = par.object_id
                        LEFT JOIN sys.types typ ON par.user_type_id = typ.user_type_id
               WHERE p.is_ms_shipped = 0
               ORDER BY s.name, p.name, par.parameter_id
               """)

    # Organize into a dictionary {proc_name: {description: txt, params: [list]}}
    procs = {}
    rows = connection.execute(sql)

    for row in rows:
        if row.full_name not in procs:
            procs[row.full_name] = {
                "description": row.description,
                "parameters": []
            }
        if row.param_name:
            procs[row.full_name]["parameters"].append(f"{row.param_name} ({row.param_type})")

    return procs