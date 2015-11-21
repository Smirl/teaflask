FROM python:3.5
EXPOSE 8000
WORKDIR /opt/app/
COPY requirements.txt /opt/app/
RUN pip install -r /opt/app/requirements.txt
COPY . /opt/app/
CMD ["/usr/local/bin/gunicorn", "manage:app", "-c", "gunicorn.py"]
