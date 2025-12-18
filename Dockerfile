# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . .
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Make port 8000 available to the world outside this container
EXPOSE 8000

RUN chmod +x /app/run.sh

ENV PYTHONPATH=/app
# Install Uvicorn for running FastAPI applications
RUN pip install uvicorn

EXPOSE 8000
# Define environment variable
CMD ["./run.sh"]