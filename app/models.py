from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, Markup, url_for
from datetime import datetime
import hashlib
from markdown import markdown
from app.exceptions import ValidationError
from . import db
from . import login_manager



##########################################################
#################         用户       ####################
##########################################################


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')

	@staticmethod
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW |
					 Permission.COMMENT, True),
			'Writer': (Permission.FOLLOW |
					   Permission.COMMENT |
					   Permission.WRITE_ARTICLES, True),
			'Administrator': (0xff, False)
		}

		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()

	def __repr__(self):
		return '<Role %r>' % self.name


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	email = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	starposts = db.relationship('Post', secondary='stars', backref=db.backref('stared', lazy='joined'), lazy='joined')
	avatar_hash = db.Column(db.String(32))
	confirmed = db.Column(db.Boolean, default=False)
	comments = db.relationship('Comment', backref='author', lazy='dynamic')
	photo = db.Column(db.String(128))

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['BLOG_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(
				self.email.encode('utf-8')).hexdigest()

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def can(self, permissions):
		return self.role is not None and (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	# 收藏/取消收藏
	def star(self, post):
		if not self.staring(post):
			s = Star(user_id=self.id, post_id=post.id)
			db.session.add(s)
			db.session.commit()

	def unstar(self, post):
		if self.staring(post):
			uns = Star.query.filter_by(user_id=self.id, post_id=post.id).first()
			db.session.delete(uns)
			db.session.commit()

	def staring(self, post):
		if Star.query.filter_by(user_id=self.id, post_id=post.id).first():
			return True
		else:
			return False

	#收藏/取消收藏


	def startimestamp(self, post):
		star = Star.query.filter_by(user_id=self.id, post_id=post.id).first()
		return star.timestamp

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)

	def __repr__(self):
		return '<User %r>' % self.username

	def to_json(self):
		json_user = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'username': self.username,
			'member_since': self.member_since,
			'last_seen': self.last_seen,
			'posts': url_for('api.get_user_posts', id=self.id, _external=True),
			'post_count': self.posts.count()
		}
		return json_user


class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False


login_manager.anonymous_user = AnonymousUser



##########################################################
#################         文章       ####################
##########################################################

class Star(db.Model):
	__tablename__ = 'stars'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
	timestamp = db.Column(db.DateTime, default=datetime.now)

	def to_json(self):
		json_star = {
			'id': self.id,
			'user_id': self.user_id,
			'post_id': self.post_id,
			'timestamp': self.timestamp
		}
		return json_star



class Post(db.Model):
	__tablename__ = 'posts'
	# __searchable__ = ['title', 'body']
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), unique=True)
	lat = db.Column(db.NUMERIC)
	long = db.Column(db.NUMERIC)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')
	photo = db.Column(db.String(128))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		target.body_html = Markup(markdown(value))

	def to_json(self):
		json_post = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'body': self.body,
			'body_html': self.body_html,
			'timestamp': self.timestamp,
			'author': url_for('api.get_user', id=self.author_id, _external=True),
			'comments': url_for('api.get_post_comments', id=self.id, _external=True),
			'comment_count': self.comments.count(),
			'photo': self.photo
		}
		return json_post

	@staticmethod
	def from_json(json_post):
		body = json_post.get('body')
		if body is None or body == '':
			raise ValidationError('post does not have a body')
		return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Category(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	posts = db.relationship('Post', backref='category', lazy='dynamic')\

	@staticmethod
	def insert_categories():
		categorylist = ["东亚观", "中亚观", "南亚观", "中亚观", "内亚观", "欧洲观", "美洲观", "非洲观", "其他"]
		for category in categorylist:
			postcategory = Category.query.filter_by(name=category).first()
			if postcategory is None:
				postcategory = Category(name=category)
				db.session.add(postcategory)
		db.session.commit()

	def __repr__(self):
		return '<Category %r>' % self.name


class Domain(db.Model):
	__tablename__ = 'domains'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	posts = db.relationship('Post', backref='domain', lazy='dynamic')

	@staticmethod
	def insert_domains():
		domainlist = ["历史", "政治", "经济", "战争", "文化", "民族", "游记", "探险", "地质", "太空"]
		for domain in domainlist:
			postdomain = Domain.query.filter_by(name=domain).first()
			if not postdomain:
				postdomain = Domain(name=domain)
				db.session.add(postdomain)
		db.session.commit()

	def __repr__(self):
		return '<Domain %r>' % self.name


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
	parent = db.Column(db.Integer, db.ForeignKey('comments.id'))
	children = db.relationship("Comment")

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		target.body_html = Markup(markdown(value))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)








