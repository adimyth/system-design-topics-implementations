# Loading Techniques in SQLAlchemy

Recently, we made a decision to make all our existing FastAPI endpoints asynchronous. One of the challenges we faced was loading data from the database. We were using SQLAlchemy as our ORM, and we had to figure out how to load data asynchronously. We were earlier using `pyscopg2` for database connections, which is synchronous. We had to switch to `asyncpg` for asynchronous database connections.

As expected, just changing the driver from `psycopg2` to `asyncpg` didn't make our code asynchronous. Unfortunately, converting from on-demand blocking query running to explicit blocking async waitpoints also requires a large conceptual refactoring of what the SQLAlchemy ORM feels like to work with. 

## Lazy Loading vs Eager Loading
Let's say we have two tables, `Author` and `Book`, where each `Author` can have multiple `Book`s. We have a one-to-many relationship between `Author` and `Book`

```python
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship('Author', backref='books')
```

In the Lazy Loading approach, when we load an `Author`, the associated `Book`s are not loaded. They are loaded only when we access the `books` attribute of the `Author`.

```python
author = session.query(Author).first()
# Books are not loaded yet - SELECT * FROM authors LIMIT 1;
books = author.books
# Books are loaded now - SELECT * FROM books WHERE author_id = author.id;
```
Here, SQLAlchemy makes an additional query to load the `Book`s associated with the `Author`.

> [!NOTE]
> From the docs - The `N+1` problem is a common side effect of the lazy load pattern, whereby an application wishes to iterate through a related attribute or collection on each member of a result set of objects, where that attribute or collection is set to be loaded via the lazy load pattern. The net result is that a `SELECT` statement is emitted to load the initial result set of parent objects; then, as the application iterates through each member, an additional `SELECT` statement is emitted for each member in order to load the related attribute or collection for that member. The end result is that for a result set of N parent objects, there will be `N+1 SELECT` statements emitted. Ex - fetching all the books of all the authors. Here, `1` query is for fetching all the authors and `N` queries are for fetching all the books of each author. Hence, `N+1` queries.

> [!IMPORTANT]
> *Lazy Loading* is the default behavior in SQLAlchemy which is synchronous. But for asynchronous applications lazy loading through relationships does not work. This throws an error - `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_() here. Was IO attempted in an unexpected place?`
> Fetching relationships data using `asyncpg` requires us to use *Eager Loading*.

In the Eager Loading approach, we load all the data in a single query. Ex - we can use the `joinedload` method to load the associated `Book`s along with the `Author`.

```python
author = session.query(Author).options(joinedload(Author.books)).first()
# Books are loaded along with the Author - SELECT * FROM authors LEFT JOIN books ON authors.id = books.author_id LIMIT 1;
```

In the above code, we are using the `joinedload` method to load the associated `Book`s along with the `Author`. This is a single query that loads all the data.

| Property                        | Lazy Loading | Eager Loading |
| ------------------------------- | ------------ | ------------- |
| Queries                         | N+1          | 1             |
| Performance                     | Slow         | Fast          |
| Memory usage                    | Low          | High          |
| Complexity                      | Low          | Medium        |
| Consistency                     | Inconsistent | Consistent    |
| Real-time data                  | Not suitable | Suitable      |
| Suitable for large datasets     | No           | Yes           |
| Suitable for complex sorting    | No           | Yes           |
| Suitable for non-sequential IDs | No           | Yes           |


## Loading Techniques (Joined Load & Selectin Load)
There are different ways to load data eagerly in SQLAlchemy, but I am interested in - `joinedload` and `selectinload`.

***SELECT IN loading*** - This form of loading emits a second (or more) `SELECT` statement which assembles the primary key identifiers of the parent objects into an `IN` clause, so that all members of related collections / scalar references are loaded at once by primary key. Example -

```python
author = session.query(Author).options(selectinload(Author.books)).first()
```

```sql
SELECT * FROM authors WHERE id IN (SELECT author_id FROM books) LIMIT 1;
```

> 🤔 Good performance for `1-1`, `1-N` & `N-1` relationships. Ex - fetching all the books of an author.

***JOINED loading*** - this form of loading applies a `JOIN` to the given `SELECT` statement so that related rows are loaded in the same result set. Example -

```python
author = session.query(Author).options(joinedload(Author.books)).first()
```

```sql
SELECT * FROM authors LEFT JOIN books ON authors.id = books.author_id LIMIT 1;
```

> 🤔 Good performance for `N-1` relationships. Ex - getting all the users belonging to a team

## Must Reads
* https://matt.sh/sqlalchemy-the-async-ening
* https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html