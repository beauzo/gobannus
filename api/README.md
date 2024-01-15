# Airplane Build Tracker API Server

This package encapsulates the FastAPI web API server.

## Debugging
Sometimes it's desirable to run the API server independently. [Hatch](https://hatch.pypa.io/latest/) must be [installed](https://hatch.pypa.io/latest/install/#pipx).

```shell
hatch run uvicorn src.api.app:app --reload
```
