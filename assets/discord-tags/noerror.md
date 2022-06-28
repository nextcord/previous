**Not getting an error, but definitely should be?**
Do you also have an `on_command_error` set up?
Please make sure to look at, and implement,** the 3 or so lines starting with 'else'** in the example below. Without this code or similar, your error handler is *eating all unhandled errors*. As you can imagine, this is bad when you get an unexpected error.
<https://gist.github.com/EvieePy/7822af90