# Database Indexes

## Problem Statement

> How to find a row in a database without an index?

Database tables are stored in a file on the disk. These are stored in pages of 8KB each. Without an index, for a given query, the database will have to scan the entire table to find the row.

1. Pull a page into memory and search for the row
2. Pull another page into memory and search for the row
3. Repeat until the row is found

This is very inefficient. This is called a **full table scan** or **sequential scan**.

**Example**: Finding a user by email in a table with 10 million users:

- Without index: Must scan all 10 million rows (could take seconds)
- With index: Jump directly to the row (milliseconds)

## Important Index Types

### B-tree Index (Most Common)

**Structure**: Balanced tree with sorted keys

**How it works:**

- Root node at top, intermediate nodes in middle, leaf nodes at bottom
- Each node contains sorted keys and pointers
- ⚡ Leaf nodes contain pointers to actual data pages
- Tree stays balanced (all leaf nodes at same depth)

**Example**: Index on `user_id`

```
         [50]
        /    \
    [25]      [75]
    /  \      /  \
[10][40] [60][90]
  ↓   ↓    ↓   ↓
[pages with actual rows]
```

**Characteristics:**

- ✅ `O(log n)` lookup time
- ✅ Supports range queries: `WHERE age BETWEEN 25 AND 35`
- ✅ Supports sorting: `ORDER BY created_at`
- ✅ Supports prefix matching: `WHERE name LIKE 'John%'`
- ✅ Works well for both equality and inequality comparisons

**When to use:**

- Columns frequently used in WHERE clauses
- Columns used in ORDER BY
- Columns used in JOINs

---

### Geospatial Indexes

Used to store and query location data (latitude & longitude).

Three types:

1. Geohashing
2. Quadtree
3. R-trees

Refer [spatial-indexing](../spatial-indexing) for more details

### GIN Index (Generalized Inverted Index)

**Purpose**: Indexes data that can have multiple values per rows. Ex - Array, JSON, etc

**When to use:**

- Array columns
- JSONB columns
- Full-text search (`tsvector`)
- Any column with composite values

Example:

```
users table:
- Alice: ['Python', 'JavaScript', 'Go']
- Bob: ['Python', 'Java']
- Charlie: ['JavaScript', 'Rust']

GIN Index creates:
Python -> [Alice, Bob]
JavaScript -> [Alice, Charlie]
Go -> [Alice]
Java -> [Bob]
Rust -> [Charlie]

Query: "Find users who know Python"
Instead of scanning all rows, GIN directly looks up "Python" -> [Alice, Bob]
```

#### Use Case 1: Array Columns

**Example**: E-commerce product with multiple tags

```sql
CREATE TABLE products (
  id INT PRIMARY KEY,
  name TEXT,
  tags TEXT[]  -- ['electronics', 'smartphone', 'android']
);

-- Without GIN: Must scan entire table
-- With GIN: Instant lookup
CREATE INDEX idx_tags ON products USING GIN(tags);

-- Now this is fast
SELECT * FROM products WHERE tags @> ARRAY['smartphone'];
SELECT * FROM products WHERE tags && ARRAY['electronics', 'laptop'];
```

#### Use Case 2: JSONB Columns

**Example**: Storing user preferences as JSON

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  preferences JSONB
);

CREATE INDEX idx_preferences ON users USING GIN(preferences);

-- Fast queries on JSON fields
SELECT * FROM users WHERE preferences @> '{"theme": "dark"}';
SELECT * FROM users WHERE preferences ? 'notifications';
SELECT * FROM users WHERE preferences -> 'language' = '"en"';
```

#### Use Case 3: Full-Text Search

```sql
CREATE TABLE articles (
  id INT PRIMARY KEY,
  title TEXT,
  content TEXT,
  search_vector tsvector
);

CREATE INDEX idx_search ON articles USING GIN(search_vector);

-- Fast full-text search
SELECT * FROM articles
WHERE search_vector @@ to_tsquery('database & (index | performance)');
```

**Characteristics:**

- ✅ Excellent for containment queries (`@>`, `?`, `&&`)
- ✅ Handles multi-value columns efficiently
- ❌ Slower to build and update than B-tree
- ❌ Larger storage overhead

## My Rule of Thumb

| Data Type                 | Index Type        |
| ------------------------- | ----------------- |
| Location Data             | GiST (Geospatial) |
| Array or JSONB            | GIN               |
| Text (full-text search)   | GIN               |
| Text (exact/prefix match) | B-tree            |
| Timestamp                 | B-tree            |
| Anything else             | B-tree            |

## Special Mention

### BRIN Index (Block Range Index)

**Purpose**: Index for **_extremely extremely large tables with natural ordering_**. Example - Time-series data

**Key Features:**

- Very small index size (1000x smaller than B-tree)
- Works well when data is naturally sorted

Example

```
Table: 1 billion log entries, 500GB
B-tree index on timestamp: 50GB (10% of table size)
BRIN index on timestamp: 50MB (0.01% of table size)

For time-range queries, BRIN is 95% as fast as B-tree
But uses 1000x less space
```

> [!NOTE] I would stick to B-tree for most cases. Only if my table size exceeds let's say 100 Million, I will use BRIN

### Hash Index

**Structure**: Hash table mapping hash values to page locations

**How it works:**

1. Run a hash function on the column we want to index
2. Store the result in a hash table
3. The hash table is a key-value pair where the key is the hash of the column value and the value is a pointer to the page containing the row

**Characteristics:**

- ✅ `O(1)` average case lookup time for exact matches
- ❌ Does NOT support range queries or sorting
- ❌ Does NOT support partial matches
- ❌ Only supports equality comparisons (`=`)

**Mostly used in in-memory stores like Redis. Not much really used in traditional databases.**

---

### Composite Index (Multi-Column)

**Purpose**: Index multiple columns together

**Example**:

```sql
CREATE INDEX idx_user_activity ON user_activity(user_id, created_at);

-- Uses the composite index efficiently
SELECT * FROM user_activity
WHERE user_id = 123
ORDER BY created_at DESC;
```

**Column order matters:**

- Index on `(user_id, created_at)` helps queries filtering by `user_id`
- But does NOT help queries filtering only by `created_at`
- Think of it like a phone book: sorted by last name, then first name

**Rule of thumb:** Put most selective (unique) columns first
