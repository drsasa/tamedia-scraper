FROM python:3.9
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

WORKDIR /
COPY req-scraper.txt ./
RUN pip install --no-cache-dir -r req-scraper.txt
RUN rm req-scraper.txt

COPY . /
WORKDIR /app
