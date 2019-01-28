import os, secrets
from PIL import Image
from flask import url_for
from flask_mail import Message

from commentaria import app, mail


def update_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)  # Randomize picture filename
    _, file_extension = os.path.splitext(form_picture.filename)  # Extract picture file type
    filename = random_hex + file_extension  # Join filename with file type
    file_path = os.path.join(app.root_path, "static/resources/profile_pictures", filename)  # Get path

    output_size = (360, 360)  # Compress target size
    i = Image.open(form_picture)
    i.thumbnail(output_size)  # Compress to target size

    i.save(file_path)  # Save to target path
    return filename  # Return saved filename


def delete_profile_picture(filename):
    if filename != "default_profile_picture.png":
        file_path = os.path.join(app.root_path, "static/resources/profile_pictures", filename)
        os.remove(file_path)


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

