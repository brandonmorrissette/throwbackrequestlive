FROM amazon/aws-lambda-python:3.9

RUN pip install boto3

WORKDIR /app

COPY create_superuser.py /app/create_superuser.py

CMD ["python3", "create_superuser.py"]
