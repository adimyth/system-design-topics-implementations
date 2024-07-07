# Code Fingerprinting
Code fingerprinting aims to produce a unique identifier (a "fingerprint") for a given piece of code or query. The idea is that similar or identical code pieces should have the same or similar fingerprints, allowing us to detect duplicates or near-duplicates efficiently.

## Steps Involved

### Normalization
This step ensures that trivial differences don't affect the fingerprint. For SQL queries, normalization might involve:
1. Converting all characters to lowercase.
2. Removing comments and whitespaces.
3. Replacing literal values (e.g., replacing specific numbers or strings with generic placeholders).

### Abstract Syntax Tree (AST) Creation
The code or query is parsed to produce an AST. An AST represents the syntactic structure of the code in a tree format, with nodes representing constructs like operations, variables, values, etc.

For SQL queries, an AST would represent the structure of the query, with nodes for `SELECT`, `WHERE`, `JOIN` clauses, and so on. ASTs abstract away from the exact textual representation and focus on the underlying logic or intent of the code.

> [!TIP]
> This is useful for semantic deduplication, where we want to detect queries that are semantically equivalent but have different textual representations.

### Hashing
The AST is hashed to produce a fingerprint. The fingerprint is a fixed-length string that uniquely identifies the AST. The fingerprint is stored in a database, along with the code or query that it represents.

### Storage & Comparison
The resulting fingerprints are stored. For duplicate detection, new fingerprints are compared to stored ones. If a match or near-match is found, it indicates a duplicate or near-duplicate piece of code or query.

## Use Cases of Fingerprinting
* **Plagiarism Detection**: Used by educators to detect if students have copied code.
* **Code Repository Management**: Detect and prevent duplicate code check-ins.
* **Malware Detection**: Identify known malicious code snippets in software.
* **Database Optimization**: Detect and cache or optimize duplicate or similar SQL queries to improve performance.
* **Software License Compliance**: Identify the use of licensed code in unauthorized places.