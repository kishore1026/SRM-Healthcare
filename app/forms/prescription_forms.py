"""Prescription forms - items are handled via JS/JSON on the frontend."""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import Optional


class PrescriptionForm(FlaskForm):
    """Prescription header form.

    Medicine items are added dynamically via JavaScript and submitted
    as a JSON string in the hidden 'items_json' field.
    """

    notes = TextAreaField(
        'Prescription Notes',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'General notes or instructions...'}
    )
    items_json = HiddenField('Items JSON')
    submit = SubmitField('Save Prescription')
