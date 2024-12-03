FROM python:3.11-slim

WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN apt update -y && apt install gcc -y

COPY . .
RUN rm -rf build
RUN poetry install


ENTRYPOINT ["poetry", "run", "dev"]