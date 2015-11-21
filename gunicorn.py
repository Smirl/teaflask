"""Python file for configuring gunicorn."""

# LOGGING
# accesslog = '-'
# errorlog = '-'
# loglevel = 'DEBUG'

bind = '0.0.0.0:80'
chdir = '/opt/app/'
graceful_timeout = 10
worker_class = 'eventlet'
workers = 2
