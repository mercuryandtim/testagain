FROM python:3.10

RUN useradd -m -u 1000 user

WORKDIR /code

# Install libgl1-mesa-glx and libglib2.0-0
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

COPY ./requirements.txt /code/requirements.txt

RUN python -m venv /code/venv

RUN /code/venv/bin/pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY --chown=user . /code

# Create necessary directories and set permissions before switching to non-root user
RUN mkdir -p /code/uploaded_videos /code/output_frames \
    && chown -R user:user /code \
    && ls -l /code

USER user

RUN ls -l /code 
RUN ls -l /code/output_frames

ENV PATH="/code/venv/bin:$PATH"
# Run app.py when the container launches using the virtual environment's Python interpreter
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7680"]
