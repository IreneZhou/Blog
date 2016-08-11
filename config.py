from os import path, environ
basedir = path.abspath(path.dirname(__file__))

MAX_SEARCH_RESULTS = 10

class Config:
	SECRET_KEY = environ.get('SECRET_KEY') or 'too young too simple +1s'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	BLOG_ADMIN = environ.get('BLOG_ADMIN')
	MAIL_SENDER = 'Blog Admin <mengyizhou94@gmail.com>'
	MAIL_SUBJECT_PREFIX = '[Blog]'
	COMMENTS_PER_PAGE = 5
	UPLOAD_FOLDER = 'app/static/images/uploads'
	ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
	WHOOSH_BASE = path.join(basedir, 'search.db')

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
	POSTS_PER_PAGE = 10
	SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'data.sqlite')


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig,
}