import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError


log = logging.getLogger(__name__)


class CourseAndEmailForm( forms.Form) :
    course_code = forms.CharField(label='Course Code', max_length=20)
    email_address = forms.EmailField(label='Email Address')

    def clean_course_code(self):
        course_code = self.cleaned_data.get('course_code')
        ## Check if course_code is empty ----------------------------
        if not course_code:
            raise forms.ValidationError("Course code cannot be empty.")
        ## Check if course_code contains more than one underscore ---
        if course_code.count('_') != 1:
            raise forms.ValidationError("Course code should contain exactly one underscore.")
        ## Split course_code into course_department and course_number
        course_department, course_number = course_code.split('_')
        ## Check that neither part is empty -------------------------
        if not course_department or not course_number:
            raise forms.ValidationError("Both course-department and course-number should be non-empty.")
        return course_code

    def clean_email_address(self):
        email_address = self.cleaned_data.get('email_address')
        # Check if email_address is empty ----------------------------
        if not email_address:
            raise forms.ValidationError("Email address cannot be empty.")
        return email_address

    ## end CourseAndEmailForm()
