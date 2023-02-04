# Namex: clean up the public namespace of your package

**Namex** is a simple utility to separate the implementation of your
Python package and its public API.

Instead of letting users access every symbol in your `.py` files,
Namex lets you create an allowlist of public symbols. You have
fully control of what they are named and under what path they
are exposed, without having to change where the code is actually located.

## Example usage

0. Make sure your codebase is correctly structured.
Your file structure should look like this
(here we use the `keras_tuner` package as an example):

```
keras_tuner_repo/
... setup.py
... keras_tuner/
...... src/  # This is your code
......... __init__.py
......... (etc)
```

If instead, it currently looks like this:

```
keras_tuner_repo/
... setup.py
... keras_tuner/
...... __init__.py
...... (etc)
```

Then you can convert your codebase by calling
`namex.convert_codebase(package="keras_tuner", code_directory="src")`
(your working directory must be `keras_tuner_repo/`).


1. Add `@export()` calls in your code:

```python
import namex

@namex.export(package="keras_tuner", path="keras_tuner.applications.HyperResNet")
class HyperResNet:
    ...
```

You can also pass a list of paths as `path`, to make
the same symbol visible under various aliases:

```python
@namex.export(
    package="keras_tuner",
    path=[
        "keras_tuner.applications.HyperResNet",
        "keras_tuner.applications.resnet.HyperResNet",
    ])
class HyperResNet:
    ...
```

2. Call `namex.generate_api_files(package="keras_tuner", code_directory="src")`
to generate API export files (your working directory must be `keras_tuner_repo/`).

3. You can now build your package as usual -- your users will only see
the symbols that you've explicitly exported, e.g. `keras_tuner.applications.HyperResNet`.

The original symbols are "hidden away" in `keras_tuners.src`.

## Why use Namex?

1. Explicit control of the namespace your users see. Don't mistakenly expose
a private utility because you didn't prefix it with an underscore!
2. Easy refactoring without having to worry where the code actually lives.
Want to move something to the `legacy/` folder but keep it
in the same place in the API? No worries.
3. Easy symbol aliasing without having to manually import an object
in a different file and having to route around circular imports.
4. Easy to spot when your public API has changed (e.g. in PR) and
easy to setup programmatic control over who can make changes
(API owners approval).
