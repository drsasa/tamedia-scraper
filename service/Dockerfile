FROM python:3.9
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

WORKDIR /
COPY req-service.txt ./
RUN pip install --no-cache-dir -r req-service.txt
RUN rm req-service.txt

COPY . /
WORKDIR /service
