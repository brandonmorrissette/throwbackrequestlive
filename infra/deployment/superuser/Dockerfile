FROM python:3.9

# Install dependencies
RUN pip install boto3 botocore

# Set working directory
WORKDIR /app

# Copy the script into the container
COPY create.py /app/create.py

# Set the default command
CMD ["python3", "/app/create.py"]
