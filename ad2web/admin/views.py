# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required

from ..extensions import db
from ..decorators import admin_required

from ..user import User
from .forms import UserForm
from ..settings import Setting


admin = Blueprint('admin', __name__, url_prefix='/settings')


#@admin.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/index.html', users=users, active='index')


@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('admin/users.html', users=users, active='users', ssl=use_ssl)


@admin.route('/user/create', methods=['GET', 'POST'], defaults={'user_id': None})
@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(user_id):
    user = User()
    form = UserForm()

    if user_id is not None:
        user = User.query.filter_by(id=user_id).first_or_404()
        form = UserForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        flash('User created.' if user_id is None else 'User updated.', 'success')
        return redirect(url_for('admin.users'))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('admin/user.html', user_id=user_id, form=form, ssl=use_ssl)

@admin.route('/user/remove/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def remove(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    users = User.query.all()
    if user_id != 1:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return redirect(url_for('admin.users'))
