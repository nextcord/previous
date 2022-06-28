**Why isn't isinstance picking up a particular exception type in my error handler?**

When an exception is raised on command invoke, it gets wrapped in `CommandInvokeError` before being thrown to an error handler (`!!error-handler`). Insert this handy expression at the top of your error handler to safely unwrap it:
```py
if isinstance(error, commands.CommandInvokeError):
  error = error.original
```
After you've unwrapped the exception, you can use `isinstance` as normal.
