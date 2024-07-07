## Scenario

> ***Imagine a multi-tenant setup where multiple client databases reside in a single RDS machine.***

Assume that your application tracks user events in our app and stores them in your transactional database in the `analytics.events` table. This can grow massively & use up a large amount of disk space in our RDS.

🤯 For one of the clients, the size of the `analytics.events` table grew at an alarming rate. Within just ***15*** ***days***, they had created ***10M*** ***records*** which used up ***15GB*** of the disk space, leaving us with ***just 4GB*** of disk space on our RDS. At this rate, it would use up the remaining disk space within a few days

💸 Increasing the disk size is not an option, as it has cost implications. 

😞 Also, you cannot reduce the disk size once you have increased it for an RDS.


## Solution
> ***With the above scenario, the idea is to keep just the most recent data (needed for ETL jobs & others) & archive (store to S3 & then delete the data from the table) the older data to free up the space.***

1. For all the client databases
   1. fetch data till `N` days ago from the `analytics.events` table. default `N` is 2 days
   2. store it in a CSV file
   3. upload the CSV to S3
   4. delete the data from the table

`N` allows us to choose how many days of data we want to keep in the table.
1. `-1` means we don't want to delete any data
2. `X` means we want to keep `X` days of data in the table
3. `default` is `2` days

## Execution
Refer to the [archive_data.py](./archive_data.py) script for the implementation details.


## Important Details
### Create index on the `triggered_at` field
Since in our where clause we are filtering data based on the `triggered_at` field, it makes sense to create an index on this field. This would help in faster retrieval of data.

We can create an index using `CREATE INDEX` as -

```sql
CREATE INDEX idx_triggered_at ON analytics.events (triggered_at);
```

🔥Unfortunately, when we create an index, Postgres requires an **AccessExclusiveLock** on the table. This prevents other transactions from performing any kind of operation (select, update, delete, etc) on this table. This would cause disruption in the system

The alternative is to use `CREATE INDEX CONCURRENTLY`

```sql
CREATE INDEX CONCURRENTLY idx_triggered_at ON analytics.events (triggered_at);
```

This acquires a **ShareUpdateExclusiveLock** on the table. This allows us to create an index on the table without necessarily blocking other operations. This operation though is a lot slower compared to the `CREATE INDEX` 

Validate the index creation by running -

```sql
-- enable amcheck extension
SHOW rds.extensions; 

CREATE EXTENSION IF NOT EXISTS amcheck;

-- fetch the index in question
SELECT * FROM pg_indexes WHERE schemaname='analytics' AND tablename='events';

-- run bt_index_check - here 'analytics.idx_triggered_at' is the index name
SELECT bt_index_check(index => 'analytics.idx_triggered_at');
```
If the index is corrupted, you will see an error message otherwise you will see a void result.


**Resources**

1. [PostgreSQL Index Creation - How it works](https://engineering.leanix.net/blog/postgres-index-creation/)
2. [Postgres Locks - A Deep Dive](https://medium.com/@hnasr/postgres-locks-a-deep-dive-9fc158a5641c)

---

### Fetch data at an hour level instead of a day level
Originally, the script was fetching data at a day level. Indexing helping in reaching the data faster, but reading the data at a day level was still slow.

So, I changed the script to fetch data at an hour level. This reduced the amount of data that we were reading at a time & made the script faster.

---

### VACUUM FULL

After running the script, the number of records in the `analytics.events` table went down from `10M` to `0.35M`. But the disk space didn't change. It was still at `4 GB`.

This is because `AUTOVACUUM` runs `VACUUM` & `ANALYZE` only

1. 🤔 `VACUUM` - This will mark the space which the deleted rows had previously acquired as available for newer rows, but it doesn't do any compaction. Basically, with `VACUUM`, it would reuse the space that the deleted rows had used previously for new rows, but the table size would remain fixed
2. `ANALYZE` - The `ANALYZE` command in PostgreSQL is used to collect statistics about the contents of tables in the database, which helps the PostgreSQL query planner to make better choices in planning queries.

To free up the disk space, we have to run `VACUUM FULL` - Vacuum Full physically deletes dead tuples and re-releases the released space to the operating system, so after vacuum full, the size of the table will be reduced to the actual space size.

`VACUUM FULL` requires an `AccessExclusiveLock` just like the index creation above. Meaning, this required downtime & we had to do it in off hours. 

```sql
-- run this in off hours as it requires an AccessExclusiveLock & will block all other operations
VACUUM FULL VERBOSE analytics.events;

-- check the size of the table
SELECT pg_size_pretty(pg_total_relation_size('analytics.events'));
```

An essential point is that to quickly iterate & validate the correctness of our script, I need a mechanism that would allow me to recreate the data locally & validate that my script was doing what it was supposed to do. **Also, it should be predictable & reproducible.**

I had created a utility script that allowed me to do this. Since, I am inserting one record per hour per day, by varying the value of `N_DAYS` in my archival script, I could predict what my database & S3 state should look like & if my script did the same.

```bash
#!/bin/bash

# Create the events table
psql -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -c "CREATE TABLE IF NOT EXISTS analytics.events (
    id SERIAL PRIMARY KEY,
    triggered_at TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL,
    os VARCHAR(255) NOT NULL,
    platform VARCHAR(255) NOT NULL,
    device VARCHAR(255) NOT NULL,
    user_details JSONB NOT NULL,
    data JSONB NOT NULL
);"

echo "Table created."

# Define the total number of hours (30 days * 24 hours)
total_hours=$((30 * 24))

# Generate data for the last 30 days, each hour
for i in $(seq 0 $((total_hours - 1))); do
    # Calculate the date and time offset by i hours ago
    if [[ "$(uname)" == "Darwin" ]]; then
        # MacOS (BSD date)
        DATE=$(date -v-"$i"H +"%Y-%m-%d %T")
    else
        # Linux (GNU date)
        DATE=$(date --date="$i hours ago" +"%Y-%m-%d %T")
    fi

    # Prepare SQL insert command
    SQL="INSERT INTO analytics.events (triggered_at, name, os, platform, device, user_details, data)
         VALUES ('$DATE', 'event_hour_$i', 'Linux', 'Web', 'Desktop', '{\"location\": \"unknown\"}', '{\"action\": \"click\", \"item\": \"hour_$i\"}');"

    # Execute the SQL command
    psql -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -c "$SQL"
done

echo "Data insertion complete."
```