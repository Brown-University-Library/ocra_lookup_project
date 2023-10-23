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
    course_code = models.CharField(max_length=20)
    email_address = models.EmailField()
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
        ## Validate that `data` field is valid JSON -----------------
        log.debug( 'starting save()' )
        if self.data:
            log.debug( 'data exists' )
            try:
                json.loads( self.data )
            except (TypeError, ValueError):
                msg = "Invalid JSON data for 'data' field."
                log.warning( f'bad data, ``{self.data}``' )
                log.exception( msg )
                raise ValidationError( msg )
        super().save(*args, **kwargs)
