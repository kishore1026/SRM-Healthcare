"""Medicine management forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField, DateField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional


DRUG_TYPE_CHOICES = [
    ('', '-- Select Drug Type --'),
    ('Tablets', 'Tablets'),
    ('Capsules', 'Capsules'),
    ('Injections', 'Injections'),
    ('Eye Drops', 'Eye Drops'),
    ('Ear Drops', 'Ear Drops'),
    ('Ointments', 'Ointments'),
]


class MedicineForm(FlaskForm):
    """Form for adding or editing a medicine."""

    medicine_name = StringField(
        'Medicine Name',
        validators=[DataRequired(message='Medicine name is required.'),
                    Length(min=2, max=200)]
    )
    drug_type = SelectField(
        'Drug Type',
        choices=DRUG_TYPE_CHOICES,
        validators=[DataRequired(message='Please select a drug type.')]
    )
    batch_number = StringField(
        'Batch Number',
        validators=[Optional(), Length(max=50)]
    )
    expiry_date = DateField(
        'Expiry Date',
        format='%Y-%m-%d',
        validators=[DataRequired(message='Expiry date is required.')]
    )
    stock_added = IntegerField(
        'Initial Stock Quantity',
        validators=[DataRequired(message='Stock quantity is required.'),
                    NumberRange(min=0, message='Stock cannot be negative.')]
    )
    submit = SubmitField('Save Medicine')


class AddStockForm(FlaskForm):
    """Form for adding stock to an existing medicine."""

    quantity = IntegerField(
        'Quantity to Add',
        validators=[DataRequired(message='Quantity is required.'),
                    NumberRange(min=1, message='Quantity must be at least 1.')]
    )
    batch_number = StringField(
        'Batch Number (optional)',
        validators=[Optional(), Length(max=50)]
    )
    expiry_date = DateField(
        'New Expiry Date (optional)',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    remarks = TextAreaField(
        'Remarks',
        validators=[Optional(), Length(max=500)]
    )
    submit = SubmitField('Add Stock')
