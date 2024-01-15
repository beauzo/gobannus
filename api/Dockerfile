FROM python:3.8

RUN apt-get update && apt-get install ffmpeg -y

WORKDIR /app

RUN python -m pip install hatch
COPY pyproject.toml ./
COPY README.md ./
COPY src ./src
RUN hatch build
RUN python -m pip install ./dist/abt_api-0.0.1-py3-none-any.whl

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0"]
