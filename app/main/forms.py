from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, Length, Optional
from ..models import Category, Domain, Topic


class LoginForm(Form):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('登录')


class PostForm(Form):
	title = StringField('标题', validators=[DataRequired(), Length(3, 64)])
	body = PageDownField(validators=[DataRequired()])
	category = SelectField('地理', coerce=int, validators=[Optional()])
	domain = SelectField('领域', coerce=int, validators=[Optional()])
	topic = SelectField('专题', coerce=int, validators=[Optional()])
	lat = DecimalField('维度', places=1)
	long = DecimalField('经度', places=1)
	photo = TextAreaField()
	submit = SubmitField("发布")

	def __init__(self, *args, **kwargs):  # 定义下拉选择表
		super(PostForm, self).__init__(*args, **kwargs)
		self.category.choices = [(category.id, category.name)
								 for category in Category.query.order_by(Category.name).all()]
		self.domain.choices = [(domain.id, domain.name)
								 for domain in Domain.query.order_by(Domain.name).all()]
		self.topic.choices = [(topic.id, topic.name)
							   for topic in Topic.query.order_by(Topic.name).all()]


class EditProfileForm(Form):
	name = StringField('真实姓名', validators=[Length(0, 12)])
	location = StringField('所在地', validators=[Length(0, 64)])
	about_me = TextAreaField("自我介绍", validators=[Length(0, 100)])
	submit = SubmitField("确认")
	photo = TextAreaField()


class CommentForm(Form):
	# body = StringField('', validators=[DataRequired()])
	body = PageDownField(validators=[DataRequired()])
	submit = SubmitField('发布')


class SearchForm(Form):
	search = StringField('搜索', validators=[DataRequired()])
	submit = SubmitField()

class TopicForm(Form):
	name = StringField('专题', validators=[DataRequired()])
