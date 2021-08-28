FROM python:3.9
WORKDIR opt/
RUN pip install poetry
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install
WORKDIR bot/
COPY . ./
CMD ["poetry", "run", "python", "main.py"]
