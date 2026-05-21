from flask_wtf import FlaskForm
from wtforms import (
    DateField, TimeField, TextAreaField, SelectField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Optional
from datetime import date, datetime


class VisitForm(FlaskForm):
    """Form for recording a new patient visit."""

    patient_id = HiddenField('Patient ID', validators=[DataRequired()])

    visit_date = DateField(
        'Visit Date',
        validators=[DataRequired(message='Visit date is required.')],
        default=date.today,
        render_kw={'class': 'form-control', 'type': 'date'}
    )

    visit_time = TimeField(
        'Visit Time',
        validators=[DataRequired(message='Visit time is required.')],
        default=lambda: datetime.now().time().replace(second=0, microsecond=0),
        render_kw={'class': 'form-control', 'type': 'time'}
    )

    doctor_id = SelectField(
        'Doctor',
        coerce=int,
        validators=[DataRequired(message='Please select a doctor.')],
        render_kw={'class': 'form-select'}
    )

    complaint = TextAreaField(
        'Chief Complaint',
        validators=[DataRequired(message='Please describe the complaint.')],
        render_kw={
            'placeholder': 'Describe the patient\'s chief complaint...',
            'class': 'form-control',
            'rows': '3'
        }
    )

    diagnosis = TextAreaField(
        'Diagnosis',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Enter diagnosis...',
            'class': 'form-control',
            'rows': '3'
        }
    )

    treatment = TextAreaField(
        'Treatment / Advice',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Treatment plan, advice given, follow-up instructions...',
            'class': 'form-control',
            'rows': '3'
        }
    )

    submit = SubmitField('Record Visit', render_kw={'class': 'btn btn-primary'})
