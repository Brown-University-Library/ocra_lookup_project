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
        label='Instructor email',
        required=True,
        # initial='',
        widget=forms.TextInput( attrs={'style': 'width:18em;'} )
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
        widget=forms.TextInput( attrs={'style': 'width:26em;'} ) 
        )

    def clean_course_code(self):
        course_code = self.cleaned_data.get( 'course_code' )
        course_code = course_code.lower().strip()
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
        email_address = email_address.lower().strip()
        # -- Check if email_address is empty ------------------------
        if not email_address:
            raise forms.ValidationError( 'Email address cannot be empty.' )
        # -- Check if email_address is valid ------------------------
        if not '@' in email_address:
            raise forms.ValidationError( 'Email address must contain an @.' )
        return email_address
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        year = year.lower().strip()
        # -- Check if year is empty ---------------------------------
        if not year:
            raise forms.ValidationError( 'Year cannot be empty.' )
        # -- Check if the string has exactly 4 characters -----------
        if len( year ) != 4:
            raise forms.ValidationError( 'Year must be exactly 4 numerals.' )    
        # -- Check that all characters are digits -------------------
        if not year.isdigit():
            raise forms.ValidationError( 'Year must be exactly 4 numerals.' )    
        # -- Check that year falls within a certain range
        year_int = int( year )
        if year_int < datetime.datetime.now().year:
            raise forms.ValidationError( "Year should not be in the past." )            
        return year

    def clean_term(self):
        term = self.cleaned_data.get('term')
        term = term.lower().strip()
        # Check if term is empty ----------------------------
        if term not in ['fall', 'spring', 'summer']:
            raise forms.ValidationError( 'Term must be either fall or spring or summer.' )
        return term
    
    def clean_course_title(self):
        course_title = self.cleaned_data.get('course_title')
        course_title = course_title.strip()
        # Check if course_title is empty ----------------------------
        if not course_title:
            raise forms.ValidationError( 'Course title cannot be empty.' )
        return course_title

    ## end CourseAndEmailForm()
