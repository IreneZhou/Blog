from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, Length
from ..models import Category


class LoginForm(Form):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('登录')


class PostForm(Form):
	title = StringField('标题', validators=[DataRequired(), Length(3, 64)])
	# category = SelectField('文章类别', coerce=int)
	lat = DecimalField('维度', places=1)
	long = DecimalField('经度', places=1)
	body = PageDownField(validators=[DataRequired()])
	submit = SubmitField("发布")

	# def __init__(self, *args, **kwargs):  # 定义下拉选择表
	# 	super(PostForm, self).__init__(*args, **kwargs)
	# 	self.category.choices = [(category.id, category.name)
	# 							 for category in Category.query.order_by(Category.name).all()]


class EditProfileForm(Form):
	name = StringField('真实姓名', validators=[Length(0, 64)])
	location = StringField('所在地', validators=[Length(0, 64)])
	about_me = TextAreaField("自我介绍")
	submit = SubmitField("确认")
	photo = TextAreaField()


class CommentForm(Form):
	# body = StringField('', validators=[DataRequired()])
	body = PageDownField(validators=[DataRequired()])
	submit = SubmitField('发布')


class SearchForm(Form):
	search = StringField('搜索', validators=[DataRequired()])
	submit = SubmitField()

