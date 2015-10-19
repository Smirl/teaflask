FROM python:3.5
RUN pip install gunicorn
EXPOSE 8000
COPY requirements.txt /opt/app/
RUN pip install -r /opt/app/requirements.txt
COPY . /opt/app/
WORKDIR /opt/app/
CMD gunicorn manage:app --log-file -
