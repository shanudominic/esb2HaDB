# Use Alpine as the base image
FROM alpine:latest

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1

# ENV ESB_MPRN=""
# ENV ESB_USERNAME=""
# ENV ESB_PASSWORD=""
# ENV ESB_GENERATED_FILENAME="esb-kwh-readings.csv"
# ENV ESB_DOWNLOAD_LOCATION="/data/"
# ENV HA_SENSOR="sensor.esb_electricity_usage"
# ENV HA_DB_FILE="/homeassistant/data/home-assistant_v2.db"
# ENV LOG_LEVEL="INFO"

# Update the package list and install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    build-base \
    && rm -rf /var/cache/apk/* 

COPY src/ /app/

WORKDIR /app/
# Create a virtual environment
RUN python3 -m venv venv
# Activate the virtual environment and install beautifulsoup4
RUN . venv/bin/activate && pip install -r requirements.txt

# Make sure the script is executable
RUN chmod +x /app/download-esb-data-upload-to-HA.sh

# Set up the cron job to run every minute
RUN echo "0 8,20 * * * /app/download-esb-data-upload-to-HA.sh >> /var/log/cron.log 2>&1" > /etc/crontabs/root

# Start cron in the foreground
CMD ["bash" , "-c", "crond -b -L /var/log/cron.log ; tail -f /var/log/cron.log"]