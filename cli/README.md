# Gobannus CLI Interface

The purpose of `gobctl` is to provide a simple CLI interface to manipulate a Gobannus cluster. At present, this minimal
CLI allows a user to add cameras, and create activity log entries.

TBD!

## Setup
* Create and activate a Python virtual environment
* Install `gobctl`: `pip install -e .`
* Run `gobctl --help` to see:
```
Usage: gobctl [OPTIONS] COMMAND [ARGS]...

  gobctl is a command line interface (CLI) for Gobannus.

Options:
  -c, --config FILE     Read option defaults from the specified INI file
                        [default: gobctl.cfg, /Users/beauzo/gobctl.cfg,
                        /Users/beauzo/.config/gobctl/config.ini]
  -v, --verbose
  -u, --url TEXT        Gobannus URL (default: "localhost")
  --api-base-path TEXT  Gobannus API base path (default: "/api")
  --version             Show the version and exit.
  --help                Show this message and exit.
```