**Got code that looks like this, and it's not working properly?**
```py
if x == "foo" or "bar" or "baz":
```
Python is interpreting this as though it was this:
```py
if (x == "foo") or ("bar") or ("baz"):
```
If the first expression (`x == "foo"`) isn't true, the second (`"bar"`) will be, so this compound conditional always passes.
Try this instead: ```py
if x == "foo" or x == "bar" or x == "baz":
``` or, even better: ```py
if x in ("foo", "bar", "baz"):
```