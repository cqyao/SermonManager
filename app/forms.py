from flask_wtf import FlaskForm
from wtforms import DateField, FileField, HiddenField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Optional, URL


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])


class AddSermonForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    speaker = StringField("Speaker", validators=[DataRequired()])
    audio_url = StringField(
        "Audio URL",
        validators=[DataRequired(), URL()],
    )
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    series_id = SelectField(
        "Sermon Series",
        coerce=int,
        choices=[("", "-- No Series --")],
        validators=[Optional()],
        default=0,
    )
    book = StringField("Book", validators=[Optional()])
    topic = StringField("Topic(s)", validators=[Optional()])
    image = FileField("Featured Image", validators=[Optional()])
    selected_image_url = HiddenField(validators=[Optional()])
