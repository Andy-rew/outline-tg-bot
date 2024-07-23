FROM python:3.10

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .
RUN mkdir ./images

# install app-specific dependencies
RUN pip install --no-cache-dir -r requirements.txt

# app command
CMD ["python", "-u", "./code/run.py"]