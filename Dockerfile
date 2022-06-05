FROM python:3.10-slim-buster

WORKDIR /bot

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-dev

COPY . .

ENTRYPOINT ["poetry", "run", "python3"]
CMD ["main.py"]
