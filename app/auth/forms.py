from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from ..models import User


class RegistrationForm(Form):
	email = StringField('邮箱', validators=[DataRequired(), Email()])
	username = StringField('用户名', validators=[DataRequired(), Length(2, 64, "用户名需在2到64字符之间")])
	password = PasswordField('密码', validators=[DataRequired(), Length(6, 128, "密码长度需在6到128位之间"), EqualTo('password2', message='两次密码不同')])
	password2 = PasswordField('确认密码', validators=[DataRequired()])
	submit = SubmitField('注册')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('啊叻,该邮箱已经注册= =')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经被占啦～')


class LoginForm(Form):
	email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField('密码', validators=[DataRequired()])
	submit = SubmitField('登录')

