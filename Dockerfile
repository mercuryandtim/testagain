FROM python:3.10

RUN useradd -m -u 1000 user

WORKDIR /code

# Install libgl1-mesa-glx and libglib2.0-0
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

COPY ./requirements.txt /code/requirements.txt

RUN python -m venv /code/venv

RUN /code/venv/bin/pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY --chown=user . /code

# Copy the start script into the container and change permissions before switching to non-root user
COPY start.sh /code/start.sh
RUN chmod +x /code/start.sh

# Create necessary directories and set permissions before switching to non-root user
RUN mkdir -p /code/uploaded_videos /code/output_frames \
    && chown -R user:user /code \
    && ls -l /code

USER user

RUN ls -l /code 
RUN ls -l /code/output_frames

ENV PATH="/code/venv/bin:$PATH"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Use the start script as the entry point
CMD ["/code/start.sh"]
