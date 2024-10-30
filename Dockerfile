# from python 3.9
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY . /app

RUN rm assets/weights/*.pth

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 ffmpeg

RUN python tools/download_models.py

RUN wget "https://up.michelecapicchioni.com/rvc/3752.pth" && mv 3752.pth assets/weights/3752.pth

CMD ["python", "api.py"]
