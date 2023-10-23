from django.db import models
import uuid


class CourseInfo( models.Model ):
    uuid = models.UUIDField( 
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        primary_key=True,
        )
    course_code = models.CharField(max_length=20)
    email_address = models.EmailField()
    data = models.JSONField(
        blank=True,
        null=True
        )

    def __str__(self):
        uuid_segment: str = '%s...' % str(self.uuid)[:8]
        display: str = f'{self.course_code}--{uuid_segment}'
        return display
