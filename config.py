import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kelogstoastcruncharepartofahealthybreakfast'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 1111
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or None
    MAIL_SUBJECT_PREFIX = '[TimeClock]'
    MAIL_SENDER = 'Records Timeclock <RTimeclock@records.nyc.gov>'
    WTF_CSRF_ENABLED = True
    ADMIN = os.environ.get('ADMIN') or 'admin@records.nyc.gov'
    EMAIL_DOMAIN = 'records.nyc.gov'

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}