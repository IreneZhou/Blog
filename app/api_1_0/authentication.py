from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from . import api
from ..models import AnonymousUser, User
from .errors import unauthorized


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
	if email == '':
		g.current_user = AnonymousUser()
		return True
	user = User.query.filter_by(email=email).first()
	if not user:
		return False
	g.current_user = user
	return  user.verify_password(password)


@api.route('/token')
def get_token():
	if g.current_user.is_anonymous() or g.token_used:
		return unauthorized('Invalid credentials')
	return jsonify({'token': g.current_user.generate_auth_token(
		expiration=3600), 'expiration': 3600})


