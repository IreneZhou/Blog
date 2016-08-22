from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form1 = LoginForm()
	if form1.validate_on_submit():
		user = User.query.filter_by(email=form1.email.data).first()
		if not user:
			flash("该邮箱不存在")
		if user and user.verify_password(form1.password.data):
			flash("登录成功", 'success')
			login_user(user)
			#return redirect(request.args.get('next') or url_for('main.index'))
			return redirect(url_for('main.user', username=user.username))
		else:
			flash('用户名或密码错误')

	form2 = RegistrationForm()
	if form2.validate_on_submit():
		user = User(email=form2.email.data, username=form2.username.data, password=form2.password.data)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		flash("注册成功")
		return redirect(url_for('main.index'))
	return render_template('auth/login.html', form1=form1, form2=form2)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('main.index'))


# @auth.before_app_request
# def before_request():
# 	if current_user.is_authenticated:
# 		if not current_user.confirmed \
# 				and request.endpoint[:5] != 'auth.' \
# 				and request.endpoint != 'static':
# 			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
# 	if current_user.confirmed:
# 		return redirect(url_for('main.index'))
# 	if current_user.confirm(token):
# 		flash("您尚未确认邮件")
# 	else:
# 		flash("链接已超时")
# 	return redirect(url_for("main.index"))


# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
# 	token = current_user.generate_confirmation_token()
# 	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
# 	flash('A new confirmation email has been sent to you by email.')
# 	return redirect(url_for('main.index'))




