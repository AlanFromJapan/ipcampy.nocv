FROM python:3.9-bookworm

# Install system dependencies
RUN apt update && apt install -y libavformat-dev libavdevice-dev python3-dev libjpeg-dev libtiff-dev zlib1g-dev

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install additional Python packages if needed
RUN pip install --no-cache-dir -r requirements.txt

#inform of the port to be exposed
EXPOSE 56780

# Copy application code
COPY . .

#Create a user to run the application NOT as root
RUN adduser --disabled-password --gecos '' --no-create-home  webuser
USER webuser

#Run the application (-u is to avoid buffering)
CMD ["python", "-u", "ipcampy.py"]
