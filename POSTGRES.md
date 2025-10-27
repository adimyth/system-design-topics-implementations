# Lock down schema for JSON / JSONB

Use `json_matches_schema` or `jsonb_matches_schema` provided by the `pg_jsonschema` to define the JSON schema definition. Then you can add a constraint on the json column using the `check` constraint.

With this -

1. we can define the field types & their allowed values
2. we can restrict storing any additional properties

Example -

```sql
ALTER TABLE {table_name}
ADD CONSTRAINT {constraint_name}
CHECK json_matches_schema(
    ... insert your schema definition here
)
```
