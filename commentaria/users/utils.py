import secrets
from flask import url_for
from flask import current_app as app
from flask_mail import Message
import cloudinary, cloudinary.uploader

from commentaria import mail


def _profile_picture_folder():
    return app.config["APP_NAME"] + "/profile_pictures/"


def update_profile_picture(form_picture):
    # Randomize picture filename
    random_filename = secrets.token_hex(8)
    # Upload image to Cloudinary
    cloudinary.uploader.upload(form_picture, public_id=random_filename, use_filename=False,
                               folder=_profile_picture_folder(),
                               transformation=[{"width": 360, "height": 360}])
    # Return saved filename
    return random_filename


def delete_profile_picture(filename):
    if filename != "default_profile_picture.png":
        result = cloudinary.uploader.destroy(_profile_picture_folder() + filename)
        app.logger.info("Cloudinary deletion: " + str(result))


def profile_picture_url(filename, params="f_auto,q_auto,fl_lossy"):
    if filename == "default_profile_picture.png":
        return url_for("static", filename="resources/profile_pictures/default_profile_picture.png")
    else:
        return "https://res.cloudinary.com/" + app.config["CLOUDINARY_CLOUD_NAME"] + "/image/upload/" \
               + params + "/" + _profile_picture_folder() + filename


def send_password_reset_email(user):
    expire_sec = 1800
    token = user.get_reset_token(expire_sec=expire_sec)
    message = Message(subject="Password Reset",
                      sender=(f"{app.config['APP_NAME']}", f"{app.config['MAIL_USERNAME']}"),
                      recipients=[user.email])
    message.body = f'''To reset your password, click the following link:
{url_for('users.reset_password_token', token=token, _external=True)}
This link will expire in {expire_sec // 60} minutes.

If you did not make this request, please ignore this email.

Please do not reply to this email address.

To contact for support, send an email to {app.config["DEV_MAIL"]}

{app.config["APP_NAME"]}
'''
    mail.send(message)
