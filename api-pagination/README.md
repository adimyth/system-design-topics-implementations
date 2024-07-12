## Setup
Imagine a products table with 100M records.
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Offset Pagination
<span style="color:yellow">**API Schema:**</span>

Request:
```json
{
  "limit": 20,
  "offset": 0
}
```

SQL Query:
```sql
SELECT * FROM products
ORDER BY id
LIMIT 20 OFFSET 0;

-- To get total count
SELECT COUNT(*) FROM products;
```


Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Product 1",
      "price": 19.99,
      "created_at": "2023-07-07T11:00:00Z"
    },
    // ... more items
  ],
  "limit": 20,
  "offset": 0,
  "total": 1000
}
```

<span style="color:green">**Pros:**</span>
* Simple to implement and understand
* Works well with SQL's LIMIT and OFFSET clauses
* Easy to jump to any page
  
<span style="color:red">**Cons:**</span>
* Performance degrades as the offset increases, especially with large datasets
* Inconsistent results if items are added or removed between page loads
* Not suitable for real-time data or frequently updated lists

<span style="color:orange">**When to use:**</span>
* Performance degrades as the offset increases, especially with large datasets
* Inconsistent results if items are added or removed between page loads
* Not suitable for real-time data or frequently updated lists


## Page Number Pagination
<span style="color:yellow">**API Schema:**</span>

Request:
```json
{
  "page": 2,
  "pageSize": 20
}
```

SQL Query:
```sql
SELECT * FROM products
ORDER BY id
LIMIT 20 OFFSET ((2 - 1) * 20);
```

Response:
```json
{
  "page": 2,
  "pageSize": 20,
  "totalItems": 1000,
  "totalPages": 50,
  "items": [
    {
      "id": 21,
      "name": "Product 21",
      "price": 29.99,
      "category": "Electronics",
      "created_at": "2023-07-07T12:00:00Z"
    },
    // ... more items
  ]
}
```

This approach is similar to offset pagination. The only difference is that the client sends the page number instead of a cursor. The server calculates the offset based on the page number and page size.

> [!NOTE]
> It has the same pros and cons as offset pagination.


## Cursor Pagination
<span style="color:yellow">**API Schema:**</span>

Request:
```json
{
  "cursor": "eyJpZCI6MjB9",
  "pageSize": 20,
  "direction": "next"
}
```
The cursor is an opaque string that encodes the last item's id. The direction indicates whether to paginate forward or backward.

SQL Query:
```sql
-- Assuming the cursor decodes to {"id": 20}
SELECT * FROM products
WHERE id > 20
ORDER BY id
LIMIT 20;
```

Response:
```json
{
  "nextCursor": "eyJpZCI6NDB9",
  "prevCursor": "eyJpZCI6MjB9",
  "pageSize": 20,
  "items": [
    {
      "id": 21,
      "name": "Product 21",
      "price": 29.99,
      "category": "Electronics",
      "created_at": "2023-07-07T12:00:00Z"
    },
    // ... more items
  ]
}
```
Here, nextCursor and prevCursor are base64 encoded JSON strings containing the last item's id and direction.

<span style="color:green">**Pros:**</span>
* Consistent results even if items are added or removed between page loads
* Suitable for real-time data or frequently updated lists
* Excellent performance even with large datasets

<span style="color:red">**Cons:**</span>
* Requires a unique, indexed column to paginate
* Cannot directly jump to a specific page
* Slightly more complex to implement than offset pagination
* Requires a sequential ordering column

<span style="color:orange">**When to use:**</span>
* Large datasets (millions of records)
* Real-time data or frequently updated lists
* Infinite scroll UIs

## Keyset Pagination
<span style="color:yellow">**API Schema:**</span>

Request:
```json
{
  "lastId": 20,
  "lastCreatedAt": "2023-07-07T11:59:59Z",
  "pageSize": 20,
  "direction": "next"
}
```

SQL Query:
```sql
SELECT * FROM products
WHERE (created_at, id) > ('2023-07-07T11:59:59Z', 20)
ORDER BY created_at, id
LIMIT 20;
```

Response:
```sql
{
  "nextKey": {"id": 40, "created_at": "2023-07-07T12:19:59Z"},
  "prevKey": {"id": 20, "created_at": "2023-07-07T11:59:59Z"},
  "pageSize": 20,
  "items": [
    {
      "id": 21,
      "name": "Product 21",
      "price": 29.99,
      "category": "Electronics",
      "created_at": "2023-07-07T12:00:00Z"
    },
    // ... more items
  ]
}
```

> [!IMPORTANT]
> The key prerequisite is that the columns used in the `WHERE` clause must match the columns used in the `ORDER BY` clause.
These columns should form a unique key for each row to ensure consistent ordering.



<span style="color:green">**Pros:**</span>
* Consistent results even if items are added or removed between page loads
* Suitable for real-time data or frequently updated lists
* Excellent performance even with large datasets
* Can paginate on multiple columns

<span style="color:red">**Cons:**</span>
* More complex to implement
* Cannot jump to a specific page
* Requires careful selection of key columns

<span style="color:orange">**When to use:**</span>
* Large datasets with complex sorting requirements
* Real-time data or frequently updated lists
* When using non-sequential IDs or composite keys

## Comparison
| Feature                         | Offset Pagination    | Page Number Pagination | Cursor Pagination | Keyset Pagination |
| ------------------------------- | -------------------- | ---------------------- | ----------------- | ----------------- |
| Performance                     | Degrades with offset | Degrades with offset   | Excellent         | Excellent         |
| Consistency                     | Inconsistent         | Inconsistent           | Consistent        | Consistent        |
| Real-time data                  | Not suitable         | Not suitable           | Suitable          | Suitable          |
| Jump to page                    | Yes                  | Yes                    | No                | No                |
| Complexity                      | Low                  | Low                    | Medium            | High              |
| Suitable for large datasets     | No                   | No                     | Yes               | Yes               |
| Suitable for complex sorting    | No                   | No                     | No                | Yes               |
| Suitable for non-sequential IDs | No                   | No                     | No                | Yes               |


> [!IMPORTANT]
> *Many products are moving away from page number based navigation to infinite scroll. Keyset pagination works well with infinite scroll UIs. Ex - Google search results.*

## Cursor vs Keyset Pagination
They both look very simiar to me. So, what's the difference between Cursor and Keyset Pagination?

1. **Encoding of pagination state:**
   - Cursor-based: Uses an opaque, encoded string (often base64) to represent the pagination state.
   - Keyset: Uses raw values from the sorted columns.

2. **Flexibility in sorting:**
   - Cursor-based: Typically uses a single column (often the primary key) for sorting.
   - Keyset: Can easily use multiple columns for complex sorting scenarios.

3. **Handling of non-sequential IDs:**
   - Cursor-based: Usually relies on sequential IDs or timestamps.
   - Keyset: Can work with non-sequential IDs or composite keys more easily.

4. **Client-side complexity:**
   - Cursor-based: Simpler for clients to handle as they just pass along an opaque string.
   - Keyset: Requires clients to handle and pass along multiple values.

5. **Server-side implementation:**
   - Cursor-based: Requires encoding/decoding of cursors on the server.
   - Keyset: Works directly with database values, potentially simpler SQL queries.

6. **Suitability for complex queries:**
   - Cursor-based: May struggle with complex sorting or filtering scenarios.
   - Keyset: More adaptable to complex queries involving multiple columns or conditions.

**Examples to Illustrate the Differences:**

1. Cursor-based Pagination:
```sql
-- Endpoint: /api/products?cursor=eyJpZCI6MTAwfQ==&limit=10

-- Server decodes cursor to {id: 100}
SELECT * FROM products
WHERE id > 100
ORDER BY id
LIMIT 10;
```

2. Keyset Pagination:

```sql
-- Endpoint: /api/products?last_id=100&last_price=50.00&limit=10

SELECT * FROM products
WHERE (price, id) > (50.00, 100)
ORDER BY price, id
LIMIT 10;
```

In this keyset example, we're paginating based on both price and id, which would be more complex with cursor-based pagination.