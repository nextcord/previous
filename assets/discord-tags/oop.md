Someone may have send this tag because you need to learn OOP.

The difference between a class and an object (*or instance*) is:

    - **A class** is the concept/blueprint of a thing, it defined what something should contain but doesn't contain any real use
    - **An object** is an actual useable thing, with the custom values, contains everything the class tells it to and you can interact with it

for example heres a `Cat` class:
```py
class Cat:
    def __init__(self, name, age=None):
        self.name = name
        self.age = age```


Now if you have a `Cat` object (instance of the `Cat` class) that lets say was constructed like `oliver = Cat("oliver", age=2)` (or was obtained from somewhere else). This oliver object has the attributes and methods we want. It can return `oliver.age` and would say it is `2` like we defined.

There are many situations in Object Oriented Programming where you will need an instance instead of a class to do something properly (in fact, you almost always need an instance instead of a class), and these cases will usually be documented.
You should learn a good amount about Object Oriented Programming before working extensively with nextcord.

One example with this is `nextcord.Guild` and `guild`, `nextcord.Guild` is the class, it does not represent any real server that exists and you can not do anything with it but says how a `guild` object should act.

Another example is `nextcord.Embed` and `embed`, `nextcord.Embed` is the class, you can construct an embed like `embed = nextcord.Embed(kwargs=here)` and you have an embed object in the variable `embed`

Read more about classes and instances here:
- <https://www.digitalocean.com/community/tutorials/understanding-class-and-instance-variables-in-python-3>
- <https://docs.python.org/3/tutorial/classes.html>
