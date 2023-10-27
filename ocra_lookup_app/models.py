import json, logging, uuid

from django.core.exceptions import ValidationError
from django.db import models

log = logging.getLogger(__name__)


class CourseInfo( models.Model ):
    uuid = models.UUIDField( 
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        primary_key=True,
        )
    course_code = models.CharField( max_length=20 )
    email_address = models.EmailField()
    year = models.CharField( max_length=4, default='YEAR' )
    term = models.CharField (max_length=10, default='TERM' )
    course_title = models.CharField (max_length=100, default='TITLE' )
    ## Note: this JSONField doesn't really do much for our servers, but if in the future they're compiled to use a JSONField, this could be useful.
    ## Note2: the JSONField doesn't auto-validate the data, hence the save() override.
    data = models.JSONField(
        blank=True,
        null=True
        )

    def __str__(self):
        uuid_segment: str = '%s...' % str(self.uuid)[:8]
        display: str = f'{self.course_code}--{uuid_segment}'
        return display

    def save(self, *args, **kwargs):
        """ Validates that `data` field is valid JSON.
            See tests.CourseInfoTest() for test-documentation. """
        log.debug( 'starting save()' )
        if self.data:
            log.debug( 'data exists' )
            try:
                json.loads( self.data )
                log.debug( 'data is valid JSON; saving' )
                super().save(*args, **kwargs)
            # except (TypeError, ValueError):
            except Exception as e:
                msg = "Invalid JSON data for 'data' field; error is: %s" % e
                log.warning( f'bad data; not saving, ``{self.data}``' )
                log.exception( msg )
                raise ValidationError( msg )
        else:
            log.debug( 'no data to validate; saving' )
            super().save(*args, **kwargs)
        

    # def save(self, *args, **kwargs):
    #     """ Validates that `data` field is valid JSON.
    #         See tests.CourseInfoTest() for test-documentation. """
    #     log.debug( 'starting save()' )
    #     if self.data:
    #         log.debug( 'data exists' )
    #         try:
    #             json.loads( self.data )
    #         except (TypeError, ValueError):
    #             msg = "Invalid JSON data for 'data' field."
    #             log.warning( f'bad data, ``{self.data}``' )
    #             log.exception( msg )
    #             raise ValidationError( msg )
    #     super().save(*args, **kwargs)
