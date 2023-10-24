import logging
from ocra_lookup_app.lib.query_ocra import QueryOcra

log = logging.getLogger(__name__)


def query_ocra( course_code: str, email_address: str ) -> dict:
    """ Queries OCRA on course_code ("HIST_1234") and email_address. 
        Called by views.results()"""
    log.debug( 'starting query_ocra()' )
    ## split course-code into dept and number -----------------------
    dept = course_code.split( '_' )[0]
    number = course_code.split( '_' )[1]
    log.debug( f'dept, ``{dept}``; number, ``{number}``' )
    ## get class-IDs for the course-code ----------------------------
    ocra = QueryOcra()
    class_ids = ocra.get_class_id_entries( dept, number )
    class_ids.sort()
    log.debug( f'class_ids, ``{class_ids}``' )
    ## get all the email-addresses for the class-IDs ----------------
    class_id_to_ocra_instructor_email_map = {}
    for class_id in class_ids:
        ## get instructor-emails from ocra ----------------------
        ocra_instructor_emails = query_ocra.get_ocra_instructor_email_from_classid( class_id )  # probably just one email, but I don't know
        if len( ocra_instructor_emails ) > 1:
            log.warning( f'whoa, more than one ocra_instructor_emails found for class_id, ``{class_id}``' )
        ocra_instructor_email = ocra_instructor_emails[0] if len(ocra_instructor_emails) > 0 else None
        ## create_map -------------------------------------------
        if ocra_instructor_email is not None:
            class_id_to_ocra_instructor_email_map[class_id] = ocra_instructor_email.strip().lower()
    log.debug( f'class_id_to_ocra_instructor_email_map, ``{class_id_to_ocra_instructor_email_map}``' )
    ## look for matches -----------------------------------------
    ocra_class_id_to_instructor_email_map_for_matches = {}
    for (class_id, ocra_instructor_email) in class_id_to_ocra_instructor_email_map.items():
        if ocra_instructor_email is None:
            continue
        else:
            if ocra_instructor_email == email_address:
                ocra_class_id_to_instructor_email_map_for_matches[class_id] = ocra_instructor_email
    log.debug( f'ocra_class_id_to_instructor_email_map_for_matches, ``{ocra_class_id_to_instructor_email_map_for_matches}``' )
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