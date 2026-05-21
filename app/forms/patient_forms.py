from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, SelectField, TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, NumberRange, Optional
)


GENDER_CHOICES = [
    ('', '-- Select Gender --'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

HOSTEL_CHOICES = [
    ('', '-- Select Hostel --'),
    ('Azad Hostel', 'Azad Hostel'),
    ('Annapurna Hostel', 'Annapurna Hostel'),
    ('Nelson Mandela Hostel', 'Nelson Mandela Hostel'),
    ('Jawaharlal Nehru Hostel', 'Jawaharlal Nehru Hostel'),
    ('MS Swaminathan Hostel', 'MS Swaminathan Hostel'),
    ('APJ Abdul Kalam Hostel', 'APJ Abdul Kalam Kalam'),
    ('Himalaya Hostel', 'Himalaya Hostel'),
    ('Vindhya Hostel', 'Vindhya Hostel'),
    ('Nilgiri Hostel', 'Nilgiri Hostel'),
    ('Cauvery Hostel', 'Cauvery Hostel'),
    ('Godavari Hostel', 'Godavari Hostel'),
    ('Other', 'Other'),
]

DESIGNATION_CHOICES = [
    ('', '-- Select Designation --'),
    ('Student', 'Student'),
    ('Staff', 'Staff'),
    ('Other', 'Other'),
]


class PatientForm(FlaskForm):
    """Form for registering a new patient with initial medicine prescription."""

    patient_name = StringField(
        'Patient Name',
        validators=[
            DataRequired(message='Patient name is required.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
        ],
        render_kw={'placeholder': 'Enter full name', 'class': 'form-control'}
    )

    age = IntegerField(
        'Age',
        validators=[
            DataRequired(message='Age is required.'),
            NumberRange(min=1, max=120, message='Age must be between 1 and 120.')
        ],
        render_kw={'placeholder': 'Enter age', 'class': 'form-control', 'min': '1', 'max': '120'}
    )

    gender = SelectField(
        'Gender',
        choices=GENDER_CHOICES,
        validators=[DataRequired(message='Please select a gender.')],
        render_kw={'class': 'form-select'}
    )

    designation = SelectField(
        'Designation',
        choices=DESIGNATION_CHOICES,
        validators=[DataRequired(message='Please select a designation.')],
        render_kw={'class': 'form-select'}
    )

    student_id = StringField(
        'Student ID Number',
        validators=[Optional(), Length(max=50)],
        render_kw={'class': 'form-control'}
    )

    hostel_name = SelectField(
        'Hostel Name',
        choices=HOSTEL_CHOICES,
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    room_number = StringField(
        'Room Number',
        validators=[Optional(), Length(max=20)],
        render_kw={'class': 'form-control'}
    )

    staff_id = StringField(
        'ID Number',
        validators=[Optional(), Length(max=50)],
        render_kw={'class': 'form-control'}
    )

    medical_history = TextAreaField(
        'Medical Information',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Known medical conditions, symptoms, diagnosis, allergies, etc.',
            'class': 'form-control',
            'rows': '4'
        }
    )

    medicine_id = SelectField(
        'Prescribed Medicine',
        coerce=int,
        validators=[DataRequired(message='Please select a medicine.')],
        render_kw={'class': 'form-select', 'id': 'medicine_id'}
    )

    quantity = IntegerField(
        'Medicine Quantity Used',
        validators=[
            DataRequired(message='Quantity is required.'),
            NumberRange(min=1, message='Quantity must be at least 1.')
        ],
        render_kw={'placeholder': 'Enter quantity', 'class': 'form-control', 'min': '1', 'id': 'quantity'}
    )

    submit = SubmitField('Register Patient', render_kw={'class': 'btn btn-primary'})


class EditPatientForm(FlaskForm):
    """Form for editing basic patient records (no prescription)."""

    patient_name = StringField(
        'Patient Name',
        validators=[
            DataRequired(message='Patient name is required.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
        ],
        render_kw={'placeholder': 'Enter full name', 'class': 'form-control'}
    )

    age = IntegerField(
        'Age',
        validators=[
            DataRequired(message='Age is required.'),
            NumberRange(min=1, max=120, message='Age must be between 1 and 120.')
        ],
        render_kw={'placeholder': 'Enter age', 'class': 'form-control', 'min': '1', 'max': '120'}
    )

    gender = SelectField(
        'Gender',
        choices=GENDER_CHOICES,
        validators=[DataRequired(message='Please select a gender.')],
        render_kw={'class': 'form-select'}
    )

    designation = SelectField(
        'Designation',
        choices=DESIGNATION_CHOICES,
        validators=[DataRequired(message='Please select a designation.')],
        render_kw={'class': 'form-select'}
    )

    student_id = StringField(
        'Student ID Number',
        validators=[Optional(), Length(max=50)],
        render_kw={'class': 'form-control'}
    )

    hostel_name = SelectField(
        'Hostel Name',
        choices=HOSTEL_CHOICES,
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    room_number = StringField(
        'Room Number',
        validators=[Optional(), Length(max=20)],
        render_kw={'class': 'form-control'}
    )

    staff_id = StringField(
        'ID Number',
        validators=[Optional(), Length(max=50)],
        render_kw={'class': 'form-control'}
    )

    medical_history = TextAreaField(
        'Medical Information',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Known medical conditions, symptoms, diagnosis, allergies, etc.',
            'class': 'form-control',
            'rows': '4'
        }
    )

    items_json = StringField('Prescription Items JSON', validators=[Optional()])

    submit = SubmitField('Update Patient', render_kw={'class': 'btn btn-warning'})
