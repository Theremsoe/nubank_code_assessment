## Code Assessment
### What contains this package?

It includes an application that resolve the code assessment required and described by Nu technical team.

### What are the requirements and dependencies of this package?

The requirements are:
 - Python 3.10 or higher
 - OS with Posix support (linux, unix)

### How can install this package?

To install we need run the following commands:
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x capital-gains
```

With all packages installed, now you can use it. Here leave a small example about how you can use it:

```bash
./capital-gains < input.txt
```

Enjoy it!

# What about testing?

To run the included tests cases we need install development dependencies. You can install them running the following command on an active ``venv`` environment:

```bash
pip install -r requirements-dev.txt
```

And then run the test site:

```bash
pytest
```
