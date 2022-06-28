Do not:
`cursor.execute("SELECT * FROM table_name WHERE value = {}".format(exampleVar))`
Or
`cursor.execute(f"SELECT * FROM table_name WHERE value = {exampleVar}")`
Do:
`cursor.execute("SELECT * FROM table_name WHERE value = ?", (exampleVar,))`

Consider: if a command accepts user input, and they input `True; DROP TABLE table_name`- The resultant query with format is:
`SELECT * FROM table_name WHERE value = True; DROP TABLE table_name` which has obvious results. 
Utilizing your SQL library's sanitization methods prepares the statement and exclusively inserts the values, without editing the query.
**Note** postgresql uses $1, $2, ... for value substitution, mysql, %s, so make sure you know your DB! 
https://xkcd.com/327
