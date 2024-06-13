FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install kafka-python
CMD ["python", "producer.py"]
