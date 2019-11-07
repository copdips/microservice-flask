FROM python:3.7
COPY . /app
RUN pip install -r /app/requirements/base.txt
RUN pip install /app/
EXPOSE 5000
CMD flask run
