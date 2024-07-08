FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create a virtual environment
RUN python -m venv venv

# Activate the virtual environment and install any needed packages specified in requirements.txt
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir -r requirements.txt"


# Run app.py when the container launches using the virtual environment's Python interpreter
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7680"]
