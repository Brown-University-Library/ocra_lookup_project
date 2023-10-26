import datetime, logging

from django import forms
# from django.conf import settings
# from django.core.exceptions import ValidationError


log = logging.getLogger(__name__)


class CourseAndEmailForm( forms.Form) :
    course_code = forms.CharField( 
        label='Course Code', 
        max_length=20, 
        required=True,
        # initial='',
        widget=forms.TextInput( attrs={'style': 'width:10em;'} )
        )
    email_address = forms.EmailField( 
        label='Email Address',
        required=True,
        )
    year = forms.CharField( 
        label='Reading-list Year', 
        max_length=4, 
        required=True, 
        # initial=str(datetime.datetime.now().year),
        widget=forms.TextInput( attrs={'style': 'width:10em;'} ) 
        )
    TERM_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ]
    term = forms.ChoiceField(label='Term', choices=TERM_CHOICES, required=True)
    course_title = forms.CharField( 
        label='Course Title', 
        max_length=100, 
        required=True, 
        # initial='TITLE',
        widget=forms.TextInput( attrs={'style': 'width:25em;'} ) 
        )

    def clean_course_code(self):
        course_code = self.cleaned_data.get( 'course_code' )
        ## Check if course_code is empty ----------------------------
        if not course_code:
            raise forms.ValidationError( 'Course code cannot be empty.' )
        ## Ensure course_code contains an underscore -----------------
        if course_code.count('_') != 1:
            raise forms.ValidationError( 'Course code should contain exactly one underscore.' )
        ## Check that neither part is empty -------------------------
        course_department, course_number = course_code.split( '_' )
        if not course_department or not course_number:
            raise forms.ValidationError( 'Both course-department and course-number should be non-empty.' )
        return course_code

    def clean_email_address(self):
        email_address = self.cleaned_data.get('email_address')
        # Check if email_address is empty ----------------------------
        if not email_address:
            raise forms.ValidationError( 'Email address cannot be empty.' )
        return email_address
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        # Check if year is empty ----------------------------
        if not year:
            raise forms.ValidationError( 'Year cannot be empty.' )
        return year

    def clean_term(self):
        term = self.cleaned_data.get('term')
        # Check if term is empty ----------------------------
        if term not in ['fall', 'spring', 'summer']:
            raise forms.ValidationError( 'Term must be either fall or spring or summer.' )
        return term

    ## end CourseAndEmailForm()
