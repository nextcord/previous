Whether you use a SQL or a NoSQL database largely depends on the type of data you need to store. SQL databases are more suited for storing relational data - data where an entry may be related to another entry, for example, a `Member` is related to its parent `Guild` - and NoSQL databases are good for storing unstructured, schema-less data. If you want to store _files_ it's recommended that you use a proper blob storage solution, such as S3, or services which are compatible with it.

In a lot of use cases SQL is the optimal choice because the the majority of data an average bot will store is highly relational data, which can be optimised and indexed effectively by a SQL database, allowing you to do complex queries and joins across tables to get exactly the data you need.

To learn about SQL we recommend you follow one of these tutorials:
SQLite - [https://www.sqlitetutorial.net/sqlite-select/](https://www.sqlitetutorial.net/sqlite-select/ "https://www.sqlitetutorial.net/sqlite-select/")
PostgreSQL - [https://www.postgresqltutorial.com/](https://www.postgresqltutorial.com/ "https://www.postgresqltutorial.com/")
MySQL - [https://www.mysqltutorial.org/](https://www.mysqltutorial.org/ "https://www.mysqltutorial.org/")

There's a vast number of NoSQL databases available, such as Redis, MongoDB, and Cassandra, so we can't hope to cover them here, but a search for one of those names should yield good information about its use cases and how to use it.
