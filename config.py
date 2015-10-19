"""Settings for the teaflask app."""

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    """Base config class."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kjasd8o701okjlasd10958uqqadrr'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'box600.bluehost.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    TEAFLASK_MAIL_SUBJECT_PREFIX = '[teaflask]'
    TEAFLASK_MAIL_SENDER = 'teaflask Admin <admin@smirlwebs.com>'
    TEAFLASK_ADMIN = ''
    TEAFLASK_PER_PAGE = 10
    TEAFLASK_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://masterbrewer:silv3rn33dl3@localhost/teaflask'

    @classmethod
    def init_app_old(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class DokkuProduction(ProductionConfig):

    """For deployment to dokku.smirlwebs.com."""

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'].replace(
        'postgres://', 'postgresql://')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'dokku-production': DokkuProduction,
    'default': DevelopmentConfig
}
