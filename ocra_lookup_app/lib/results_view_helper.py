import logging

log = logging.getLogger(__name__)


def query_ocra( course_code: str, email_address: str ) -> dict:
    return {}


def make_context( request, course_code: str, email_address: str, data: dict ) -> dict:
    """ Builds context for results view.
        Called by views.results() """
    context = {
        'course_code': course_code,
        'email_address': email_address,
        'data': data
    }
    log.debug( f'context-keys, ``{list(context.keys())}``' )
    return context