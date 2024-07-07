## Overview
1. `VACUUM` is a *SQL command* that performs certain maintenance operations.
2. `AutoVacuum` is a set of background processes that automatically run the *VACUUM* and *ANALYZE* operations.

## What does `VACUUM` do?
1. `VACUUM` reclaims storage occupied by deleted rows and the old versions of updated rows. If this is not done, your table and indexes will bloat & the database will become unreasonably large.
2. `VACUUM` allows for reusability of transaction ids - `XID`s & `MXIDs`. If this is not done, the database will run out of transaction ids & will stop accepting new transactions. Transaction IDs is a limited resource which should be recycled.
3. `VACUUM` also updates the visibility map, which is used to determine which rows are visible to transactions. This makes future vacuum operations faster as well as index scans.

## How does `AUTOVACUUM` work?
1. There is an an `autovacuum launcher` which runs all the time
2. It keeps track of what DB exits and regularly starts *autovacuum worker* processes in each database.
3. The `autovacuum worker` looks at each table in the database (to which it can connect to) & decides whether to perform `VACUUM` or `ANALYZE` on that table. It can run both or either of them or none.

## What can go wrong?
1. autovacuum is just a system for running `VACUUM` & `ANALYZE` commands automatically according to a set of configurable parameters.
2. If these configurations aren't set properly, autovacuum may work correctly but fail to achieve the intended goals.
3. autovacuum thinks tables need to be vacuumed when they really don't need to be vacuumed.
4. autovacuum thinks tables don't need to be vacuumed when they really do need to be vacuumed.
5. Any problem with `VACUUM` or `ANALYZE` also affects autovacuum.   
    This typically happens because `VACUUM` could face some issues (more so than `ANALYZE`), like:
    1. Could fail: If the table is locked by another transaction, `VACUUM` will fail.
    2. Could run forever
    3. Could run for a really long time: If the table is really large, `VACUUM` could take a long time to complete.

All of these can really happen as it can happen for any other SQL command like `SELECT`, `UPDATE`, `DELETE`, etc. 

## VACUUM is running forever
1. Table is really large - be patient
2. VACUUM is blocked by another transaction - check `pg_stat_activity` to see if there are any long-running transactions
3. Disk is too slow - upgrade your disk
4. Your indexes are bloated/corrupted - run `REINDEX` on the table

Increase `vacuum_cost_limit` to make `VACUUM` faster.