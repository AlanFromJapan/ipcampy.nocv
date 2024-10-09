FROM python:3.9-bookworm

COPY . /app

WORKDIR /app

RUN apt update && apt install -y libavformat-dev libavdevice-dev python3-dev libjpeg-dev libtiff-dev zlib1g-dev

RUN pip install -r requirements.txt

#inform of the port to be exposed
EXPOSE 56780

#Create a user to run the application NOT as root
RUN adduser --disabled-password --gecos '' --no-create-home  webuser
USER webuser

#Run the application (-u is to avoid buffering)
CMD ["python", "-u", "ipcampy.py"]
