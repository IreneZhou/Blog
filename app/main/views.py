import os
from flask import render_template, abort, session, redirect, url_for, request, flash, g, jsonify
from flask_login import current_user, current_app, login_required
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.utils import secure_filename
from . import main
from .. import db, admin
from flask_admin.contrib.sqla import ModelView
from .forms import LoginForm, PostForm, CommentForm, EditProfileForm, SearchForm
from ..models import User, Post, Permission, Comment, Star, Role
import base64



@main.route('/')
@main.route('/index')
def index():
	form = SearchForm()
	# category_list = Category.query.all()
	# star = Star.query.with_entities(Star.post_id).all()
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	posts = pagination.items
	all_posts = Post.query.all()
	return render_template('index.html', posts=posts, pagination=pagination, user=user, star=star, form=form, all_posts=all_posts)


@main.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	return render_template('login.html', form=form, title="加入")


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author_id=user.id).order_by(Post.timestamp.desc())
	return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		# file = request.files['file']
		if form.photo.data:
		# if file:
			val = form.photo.data[22:]
			filestring = base64.b64decode(val)
			filename = os.path.join(current_app.config['PROFILE_FOLDER']) + '/' + str(current_user.id) + '.png'
			file = open(filename, "wb")
			file.write(filestring)
			current_user.photo = '..' + filename[3:]
		db.session.add(current_user)
		db.session.commit()
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@main.route('/write', methods=['GET', 'POST'])
@login_required
def write():
	if not current_user.can(Permission.WRITE_ARTICLES):
		flash("抱歉，您暂时没有发布权限")
	all_posts = Post.query.all()
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('没有上传题图')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
		post = Post(body=form.body.data, title=form.title.data, lat=form.lat.data, long=form.long.data,
					author=current_user._get_current_object(),
					photo=os.path.join("static/images/uploads/", filename))
		db.session.add(post)
		try:
			db.session.commit()
			flash("成功发布!")
			return redirect(url_for('main.post', id=post.id))
		except IntegrityError:
			db.session.rollback()
			flash("发布失败")
	return render_template('write.html', form=form, all_posts=all_posts)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	all_posts = Post.query.all()
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.lat = form.lat.data
		post.long = form.long.data
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('main.post', id=post.id))
	form.body.data = post.body
	form.title.data = post.title
	form.lat.data = post.lat
	form.long.data = post.long
	return render_template('write.html', form=form, all_posts=all_posts)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	post = Post.query.get_or_404(id)
	commentForm = CommentForm()
	if commentForm.validate_on_submit() and current_user.is_authenticated:
		comment = Comment(body=commentForm.body.data,
						  post=post,
						  author=current_user._get_current_object())
		db.session.add(comment)
		flash('Your comment has been published.')
		return redirect(url_for('.post', id=post.id, page=-1))
	# page = request.args.get('page', 1, type=int)
	# if page == -1:
	# 	page = (post.comments.count() - 1) / current_app.config['COMMENTS_PER_PAGE'] + 1
	# pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config[
	# 'COMMENTS_PER_PAGE'], error_out=False)
	#
	# comments = pagination.items
	comments = post.comments.order_by(Comment.timestamp.asc())
	return render_template('post.html', post=post, commentForm=commentForm, form=SearchForm(), comments=comments)


#收藏
@main.route('/star/<int:id>')
@login_required
def star(id):
	post = Post.query.get_or_404(id)
	if current_user.staring(post):
		current_user.unstar(post)
	else:
		current_user.star(post)


@main.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()


@main.route('/search', methods=['POST'])
def search():
	if not SearchForm().validate_on_submit():
		return redirect(url_for('.index'))
	return redirect(url_for('.search_results', query=SearchForm().search.data))


@main.route('/search_results/<query>')
def search_results(query):
	form = SearchForm()
	results = Post.query.filter(Post.title.like('%' + query + '%')).all()
	return render_template('search_results.html', query=query, results=results, form=form)



class MyView(ModelView):
	def is_accessible(self):
		return current_user.is_administrator()


admin.add_view(MyView(User, db.session))
admin.add_view(MyView(Post, db.session))
admin.add_view(MyView(Comment, db.session))
admin.add_view(MyView(Role, db.session))


