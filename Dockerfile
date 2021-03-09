# docker build --tag repository:new_tag .
# or
# docker build --tag repository . && docker tag repository:latest repository:new_tag

FROM python:3.9.2-slim-buster
# for better performance: FROM ubuntu:20.04

WORKDIR /app
COPY . .
RUN pip install -r ./requirements/base.txt
RUN pip install .
EXPOSE 5000
CMD ["flask", "run"]
