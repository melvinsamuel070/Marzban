ARG PYTHON_VERSION=3.12

FROM python:$PYTHON_VERSION-slim AS build

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl unzip gcc python3-dev libpq-dev \
    && curl -L https://github.com/Gozargah/Marzban-scripts/raw/master/install_latest_xray.sh | bash \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/
RUN python3 -m pip install --upgrade pip \
    && pip install --no-cache-dir --user -r /code/requirements.txt

FROM python:$PYTHON_VERSION-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /code

# Copy the user installation directory directly to match global paths safely
COPY --from=build /root/.local /root/.local
COPY --from=build /usr/local/share/xray /usr/local/share/xray

# Bind the user binary paths to the runtime path environment
ENV PATH=/root/.local/bin:$PATH

COPY . /code

RUN ln -s /code/marzban-cli.py /usr/bin/marzban-cli \
    && chmod +x /usr/bin/marzban-cli \
    && marzban-cli completion install --shell bash

CMD ["bash", "-c", "alembic upgrade head; python main.py"]