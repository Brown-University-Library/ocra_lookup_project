import json, logging

# from django.test import SimpleTestCase as TestCase    # SimpleTestCase does not require db
from django.conf import settings as project_settings
from django.core.exceptions import ValidationError
from django.test import TestCase                        # TestCase requires db
from django.test.utils import override_settings
from ocra_lookup_app.models import CourseInfo


log = logging.getLogger(__name__)
TestCase.maxDiff = 1000


class ErrorCheckTest( TestCase ):
    """ Checks urls. """

    @override_settings(DEBUG=True)  # for tests, DEBUG autosets to False
    def test_dev_errorcheck(self):
        """ Checks that dev error_check url triggers error.. """
        log.debug( f'debug, ``{project_settings.DEBUG}``' )
        try:
            log.debug( 'about to initiate client.get()' )
            response = self.client.get( '/error_check/' )
        except Exception as e:
            log.debug( f'e, ``{repr(e)}``' )
            self.assertEqual( "Exception('Raising intentional exception.')", repr(e) )

    def test_prod_errorcheck(self):
        """ Checks that production error_check url returns 404. """
        log.debug( f'debug, ``{project_settings.DEBUG}``' )
        response = self.client.get( '/error_check/' )
        self.assertEqual( 404, response.status_code )


class CourseInfoTest( TestCase ):
    """ Checks CourseInfo model. """

    def test_courseinfo(self):
        """ Checks that CourseInfo data field accepts valid json, and rejects invalid json. """
        ## Valid json -----------------------------------------------
        valid_json = json.dumps( {'foo':'bar'} )
        courseinfo = CourseInfo( course_code='foo_bar', email_address= 'z@z.edu', data=valid_json )
        courseinfo.save()
        courseinfo.refresh_from_db()
        self.assertEqual( valid_json, courseinfo.data )
        ## Invalid json ---------------------------------------------
        invalid_json = 42
        courseinfo = CourseInfo( course_code='foo_bar', email_address= 'z@z.edu', data=invalid_json )
        with self.assertRaises( ValidationError ):
            courseinfo.save()
        ## More invalid json ---------------------------------------------
        invalid_json = {'some_key':'some_val'}
        courseinfo = CourseInfo( course_code='foo_bar', email_address= 'z@z.edu', data=invalid_json )
        with self.assertRaises( ValidationError ):
            courseinfo.save()
        ## No json --------------------------------------------------
        courseinfo = CourseInfo( course_code='foo_bar', email_address= 'z@z.edu', data=None )
        courseinfo.save()
        courseinfo.refresh_from_db()
        self.assertEqual( None, courseinfo.data )
        ## Empty json --------------------------------------------------
        courseinfo = CourseInfo( course_code='foo_bar', email_address= 'z@z.edu', data='' )
        courseinfo.save()
        courseinfo.refresh_from_db()
        self.assertEqual( '', courseinfo.data )
