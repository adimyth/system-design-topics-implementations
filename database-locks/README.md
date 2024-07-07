## Postgres Locks

PostgreSQL uses a variety of locks to manage concurrent access to data. Understanding these locks is crucial for designing efficient and scalable database applications. This guide provides an overview of the different types of locks in PostgreSQL and how they interact with various database operations.

A very good read here - https://medium.com/@hnasr/postgres-locks-a-deep-dive-9fc158a5641c

Assume a table named `users`

## Data Manipulation Language (DML) Operations 

### SELECT
- Lock Acquired: ACCESS SHARE
- Effect: 
    * Allows concurrent reads and writes on all rows.
    * Multiple SELECTs can run simultaneously on the same table or even the same row.
- What happens: Other transactions can freely read from and write to the `users` table.

### UPDATE, DELETE, INSERT
- Lock Acquired: ROW EXCLUSIVE
- Effect:
  * Locks only the specific rows being modified.
  * Allows concurrent reads on all rows, including the locked ones.
  * Allows concurrent writes on other rows not being modified.
- What happens:
  * For UPDATE and DELETE: Only the specific rows being modified are locked for writing. Other transactions can still read these rows and can read/write to all other rows concurrently.
  * For INSERT: No existing rows are locked. The new row being inserted is locked until the transaction completes.
  * Multiple UPDATEs, DELETEs, and INSERTs can occur concurrently as long as they don't target the same rows.

> [!NOTE]
> When a row is being updated, PostgreSQL uses a multi-version concurrency control (MVCC) system. Other transactions will see the previous version of the row until the updating transaction commits. So, concurrent reads are allowed, but they see the pre-update version of the data.

### SELECT FOR UPDATE / SELECT FOR SHARE
- Lock Acquired: ROW SHARE
- Effect:
    * Locks specific rows for potential updates.
    * Allows reads on all rows, including the locked ones.
    * May block writes on the locked rows, depending on the type of lock (UPDATE vs SHARE).
- Example
    ```sql
    BEGIN;
    SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
    -- (balance is 500, for example)
    -- Do some application-level logic
    UPDATE accounts SET balance = 400 WHERE id = 1;
    COMMIT;
    ```
- What happens:
  * The specified rows are locked.
  * Other transactions can read the locked rows but cannot modify them until the lock is released.
  * All other rows remain fully accessible for both reads and writes.

## Data Definition Language (DDL) Operations

### CREATE INDEX
Without CONCURRENTLY:
 * Lock Acquired: SHARE
 * Effect: Allows concurrent reads but blocks all writes to the entire table.
 * Example: `CREATE INDEX ON users(email);`
 * What happens: Other transactions can read from the `users` table, but all write operations (INSERT, UPDATE, DELETE) will be blocked until the index creation is complete.

With CONCURRENTLY:
  * Lock Acquired: SHARE UPDATE EXCLUSIVE
  * Effect: Allows concurrent reads and row-level writes, but blocks operations that would take conflicting table-level locks.
  * Example: `CREATE INDEX CONCURRENTLY ON users(email);`
  * What happens: The table can still be read from and written to by other transactions, but operations like ALTER TABLE will be blocked.

### CREATE, ALTER, RENAME, TRUNCATE, DROP TABLE
- Lock Acquired: ACCESS EXCLUSIVE
- Effect: Blocks all concurrent operations on the table.
- What happens: No other transaction can access the `users` table in any way until the current operation completes. All SELECTs, UPDATEs, INSERTs, and DELETEs will be blocked.

## Data Control Language (DCL) Operations
### GRANT, REVOKE
Typically doesn't acquire a table lock, but may briefly lock the system catalog

## Transaction Control Language (TCL) Operations
### BEGIN, COMMIT, ROLLBACK
* COMMIT: Doesn't acquire additional locks, releases existing transaction locks
* ROLLBACK: Doesn't acquire additional locks, releases existing transaction locks

## Maintenance Operations:

### VACUUM, ANALYZE
- Lock Acquired: SHARE UPDATE EXCLUSIVE
- Effect:
  * Allows concurrent reads and row-level writes.
  * Blocks operations that would take conflicting table-level locks.
- Examples:
  * `VACUUM users;`
  * `ANALYZE users;`
- What happens: The table can still be read from and written to by other transactions, but operations like ALTER TABLE or regular CREATE INDEX will be blocked.

### CLUSTER, REINDEX
- Lock Acquired: ACCESS EXCLUSIVE
- Effect: Blocks all concurrent operations on the table.
- Examples:
  * `CLUSTER users USING users_pkey;`
  * `REINDEX TABLE users;`
- What happens: No other transaction can access the `users` table in any way until this operation completes.

## Summary of PostgreSQL Lock Types

### 1. ACCESS SHARE
* Acquired by: SELECT
* Effect: Most permissive, allows all operations except those requiring ACCESS EXCLUSIVE
* Example: `SELECT * FROM users WHERE age > 18;`

### 2. ROW SHARE
* Acquired by: SELECT FOR UPDATE, SELECT FOR SHARE
* Effect: Allows concurrent reads and most writes, conflicts with EXCLUSIVE and ACCESS EXCLUSIVE
* Example: `SELECT * FROM users WHERE id = 1 FOR UPDATE;`

### 3. ROW EXCLUSIVE
* Acquired by: UPDATE, DELETE, INSERT
* Effect: Locks only specific rows being modified, allows concurrent operations on other rows
* Example: `UPDATE users SET last_login = NOW() WHERE id = 1;`

### 4. SHARE UPDATE EXCLUSIVE
* Acquired by: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY
* Effect: Allows concurrent reads and row-level writes, conflicts with SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, and ACCESS EXCLUSIVE
* Example: `VACUUM users;`

### 5. SHARE
* Acquired by: CREATE INDEX (without CONCURRENTLY)
* Effect: Allows concurrent reads, blocks all writes
* Example: `CREATE INDEX ON users(email);`

### 6. SHARE ROW EXCLUSIVE
* Acquired by: Certain ALTER TABLE operations
* Effect: Allows only concurrent read-only queries
* Example: Rarely used directly, part of some complex ALTER TABLE operations

### 7. EXCLUSIVE
* Rarely used directly, can be explicitly acquired
* Effect: Allows only concurrent SELECTs, blocks all other operations
* Example:
  ```sql
  BEGIN;
  LOCK TABLE users IN EXCLUSIVE MODE;
  -- operations here
  COMMIT;

### 8. ACCESS EXCLUSIVE
* Acquired by: ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX (table), CLUSTER
* Effect: Blocks all operations on the table, including SELECTs
* Example: ALTER TABLE users ADD COLUMN age INTEGER;