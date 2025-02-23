from django import forms
from datetime import date, timedelta

from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import *
from django.db import connection
from django.db.models import Subquery, Q, Case, When, F, Value, CharField
from django.db.models.functions import Concat

#Form Layout from Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import modelformset_factory


class DocFileUploadForm(forms.Form):
    document = forms.FileField(
        label='Select Document File',
        help_text='(upload .pdf file)'
    )
    
    def clean_document(self):
        document = self.cleaned_data['document']
        
        # Validate file extension
        if not document.name.endswith('.pdf'):
            raise forms.ValidationError('Only .pdf files are allowed')
            
        # Validate file size (e.g., max 10MB)
        if document.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File size must be under 10MB')
            
        return document