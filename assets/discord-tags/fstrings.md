**F-Strings** are available in Python3.6+.
An **F-String** is a Formatted String Literal.

**Docs:** <https://docs.python.org/3/reference/lexical_analysis.html#formatted-string-literals>
**PEP:** <https://www.python.org/dev/peps/pep-0498>

**__Example__**
**Our Variable:**
```py
user_name = "Ebic#6969"
```
**Not using F-String:**
```py
# % Operator, very old
print("Hello %s!" % user_name)

# str.format
print("Hello !".format(user_name))

# + Operator
print("Hello " + user_name + "!")

# Positional Arguments
print("Hello ", user_name, "!")
```
**Using F-Strings:**
```py
print(f"Hello \{\user_name\}\!")
```
**More about string formatting:** <https://realpython.com/python-string-formatting>
