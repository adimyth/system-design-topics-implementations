# How JOIN works in PostgreSQL

## Setup
I have 2 tables - `users_meta_data` and `user_metrics_aggregates`. I want to join these tables and get the sum of `total_clicks` for each `user_designation` where `time_unit='Day'`.

1. `users_meta_data` has 15K rows and `user_metrics_aggregates` has 2.5M rows.
2. There are 3 unique `user_designation` values - Admin, User and Guest.
3. There are 2 unique `time_unit` values - Day, Week and Month.
4. There are ~1.3M rows where `time_unit='Day'`.

```sql
EXPLAIN ANALYZE SELECT user_designation, SUM(total_clicks) AS "SUM(total_clicks)"
FROM
  (SELECT *
   FROM analytics.users_meta_data AS umd
   JOIN analytics.user_metrics_aggregates AS uma ON umd.user_id = uma.user_id) AS virtual_table
WHERE time_unit='Day'
GROUP BY user_designation;
```

Response
```sql
Finalize GroupAggregate  (cost=64441.03..64441.79 rows=3 width=15) (actual time=1943.689..1948.749 rows=4 loops=1)
  Group Key: umd.user_designation
  ->  Gather Merge  (cost=64441.03..64441.73 rows=6 width=15) (actual time=1943.676..1948.736 rows=12 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        ->  Sort  (cost=63441.01..63441.01 rows=3 width=15) (actual time=1934.563..1934.568 rows=4 loops=3)
              Sort Key: umd.user_designation
              Sort Method: quicksort  Memory: 25kB
              Worker 0:  Sort Method: quicksort  Memory: 25kB
              Worker 1:  Sort Method: quicksort  Memory: 25kB
              ->  Partial HashAggregate  (cost=63440.95..63440.98 rows=3 width=15) (actual time=1934.519..1934.525 rows=4 loops=3)
                    Group Key: umd.user_designation
                    Batches: 1  Memory Usage: 24kB
                    Worker 0:  Batches: 1  Memory Usage: 24kB
                    Worker 1:  Batches: 1  Memory Usage: 24kB
                    ->  Hash Join  (cost=1045.25..60650.65 rows=558060 width=11) (actual time=24.280..1827.686 rows=447000 loops=3)
                          Hash Cond: (uma.user_id = umd.user_id)
                          ->  Parallel Seq Scan on user_metrics_aggregates uma  (cost=0.00..51932.08 rows=558060 width=20) (actual time=0.632..1671.710 rows=447000 loops=3)
                                Filter: ((time_unit)::text = 'Day'::text)
                                Rows Removed by Filter: 377467
                          ->  Hash  (cost=859.00..859.00 rows=14900 width=23) (actual time=23.458..23.459 rows=14900 loops=3)
                                Buckets: 16384  Batches: 1  Memory Usage: 938kB
                                ->  Seq Scan on users_meta_data umd  (cost=0.00..859.00 rows=14900 width=23) (actual time=0.290..20.391 rows=14900 loops=3)
Planning Time: 6.388 ms
Execution Time: 1948.827 ms
```

## Explanation
1️⃣ Join is happening using the `Hash Join` algorithm. It works by hashing the join keys of the two tables and then comparing the hash values. This is a very efficient way to join tables. Refer [hash join](#hash-join) for more details.


```sql
Hash Join  (cost=1045.25..60650.65 rows=558060 width=11) (actual time=24.280..1827.686 rows=447000 loops=3)
```

The join took 1.8s to complete
```sql
actual time=24.280..1827.686 rows=447000 loops=3
```

2️⃣ It creates a hash table for the smaller table (`users_meta_data`). It is doing a sequential scan on the `users_meta_data` table to create a hash table.
```sql
->  Hash  (cost=859.00..859.00 rows=14900 width=23) (actual time=23.458..23.459 rows=14900 loops=3)
        Buckets: 16384  Batches: 1  Memory Usage: 938kB
        ->  Seq Scan on users_meta_data umd  (cost=0.00..859.00 rows=14900 width=23) (actual time=0.290..20.391 rows=14900 loops=3)"
```
It took 20ms to scan the table and create the hash table.
```sql
actual time=0.290..20.391 rows=14900 loops=3
```
It occupied 938KB of memory.
```sql
Memory Usage: 938kB
```

---

3️⃣ It then scans the larger table (`user_metrics_aggregates`) and for each row, it hashes the join key and looks up the hash table to find the matching rows.
```sql
->  Parallel Seq Scan on user_metrics_aggregates uma  (cost=0.00..51932.08 rows=558060 width=20) (actual time=0.632..1671.710 rows=447000 loops=3)
        Filter: ((time_unit)::text = 'Day'::text)
        Rows Removed by Filter: 377467
```

---

4️⃣ In both the steps, loops=3, because I have the value for `max_parallel_workers_per_gather` set to 2. There is 1 main process and 2 parallel workers. 

Here, each worker is scanning a part of the table. I had 1.3M rows where `time_unit='Day'`, so each worker is scanning ~433K rows.
```sql
(actual time=0.632..1671.710 rows=447000 loops=3)
Rows Removed by Filter: 377467
```

---
5️⃣ No index is being used in this query. The query planner decided that a hash join would be faster than a merge join.

```sql
Hash Join  (cost=1045.25..60650.65 rows=558060 width=11) (actual time=24.280..1827.686 rows=447000 loops=3)
```



## JOIN Algorithms

### Nested Loop Join
For each row in the outer table, scans the entire inner table. It is the slowest join algorithm. The time complexity is `O(M * N)`, where M & N is the number of rows in the two tables.

### Merge Join
The time complexity of the merge join algorithm is `O(M * log(M) + N * log(N))`, where M & N is the number of rows in the two tables. It is faster than the nested loop join but slower than the hash join.

It works by sorting the two tables on the join key and then merging the two sorted tables. ***It is efficient when the join keys are indexed.***


### Hash Join
The time complexity of the hash join algorithm is `O(M + N)`, where M & N is the number of rows in the two tables. It is the most efficient join algorithm.
* `O(M)` - to create the hash table for the smaller table.
* `O(N)` - to scan the larger table and look up the hash table to find the matching rows.

PostgreSQL typically builds the hash table from the smaller table for efficiency.


> [!IMPORTANT]
> The hash join algorithm is used when the join condition is an equality operator. It is also used when the join condition is a non-equality operator, but the query planner decides that a hash join would be faster than a merge join.


## Hash Table
A hash table is a data structure that stores key-value pairs. It works by hashing the key and then storing the value at the hashed index. It is very efficient for lookups. Example -

PostgreSQL uses a hash table to store the join keys of the smaller table. It then scans the larger table and for each row, it hashes the join key and looks up the hash table to find the matching rows.

Allows for `O(1)` average case lookup time during the join operation.

## Questions
1️⃣ Why would the query planner choose a hash join over a merge join?

Hash join is not always the fastest. It requires building a hash table for the smaller table. If the hash table is too large to fit in memory, then the hash join will be slower than a merge join. The query planner decides whether to use a hash join based on the size of the tables and the cost of the query.

* For very small tables, Nested Loop can be faster. 
* For pre-sorted data, Merge Join can be more efficient. 
* Hash Joins are not ideal for inequality joins (e.g., WHERE a.id < b.id).

2️⃣ Why would the query planner choose a sequential scan over parallel scan?

For smaller tables, the overhead of parallelism can outweigh the benefits of parallelism. The query planner decides whether to use parallelism based on the size of the table and the cost of the query.

3️⃣ Why would the database not use indexes to join tables?

The query planner decides whether to use an index based on the cost of the query. If the cost of using an index is higher than a sequential scan, then the query planner will choose a sequential scan.


