FROM python:3.5
EXPOSE 8000
WORKDIR /opt/app/
COPY requirements.txt /opt/app/
RUN pip install -r /opt/app/requirements.txt
COPY . /opt/app/
CMD gunicorn manage:app --bind 0.0.0.0:8000 \
						--worker-class eventlet \
						--workers 2 \
						--log-level INFO \
						--access-logfile - \
						--error-logfile -
