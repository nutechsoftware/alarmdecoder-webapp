from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, Markup, redirect
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..user import User
from ..settings.models import Setting
from alarmdecoder.panels import ADEMCO, DSC
from ..keypad.models import KeypadButton
from .forms import CameraForm
from .models import Camera

cameras = Blueprint('cameras', __name__, url_prefix='/cameras')

@cameras.route('/')
@login_required
def index():
    camera_list = Camera.query.filter_by(user_id=current_user.id).all()
    buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    return render_template('cameras/index.html', camera_list=camera_list, buttons=buttons, ssl=use_ssl)

@cameras.route('/camera_list')
@login_required
def cam_list():
    camera_list = Camera.query.filter_by(user_id=current_user.id).all()
    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('cameras/cam_list.html', camera_list=camera_list, ssl=use_ssl, active="cameras")

@cameras.route('/create_camera', methods=['GET', 'POST'])
@login_required
def create_camera():
    use_ssl = Setting.get_by_name('use_ssl',default=False).value

    form = CameraForm()
    
    if form.validate_on_submit():
        cam = Camera()
        form.populate_obj(cam)
        cam.user_id = current_user.id

        db.session.add(cam)
        db.session.commit()
        flash('Camera Created', 'success')
        return redirect(url_for('cameras.cam_list'))

    return render_template('cameras/create_cam.html', form=form, active="cameras", ssl=use_ssl)

@cameras.route('/edit_camera/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_camera(id):
    cam = Camera.query.filter_by(id=id,user_id=current_user.id).first_or_404()
    form = CameraForm(obj=cam)

    if form.validate_on_submit():
        form.populate_obj(cam)
        cam.user_id = current_user.id

        db.session.add(cam)
        db.session.commit()

        flash('Camera Updated', 'success')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    return render_template('cameras/edit_cam.html', form=form, id=id, active="cameras", ssl=use_ssl)

@cameras.route('/remove_camera/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_camera(id):
    cam = Camera.query.filter_by(id=id,user_id=current_user.id).first_or_404()

    db.session.delete(cam)
    db.session.commit()

    flash('Camera Removed', 'success')
    return redirect(url_for('cameras.cam_list'))
