import logging, pprint
from ocra_lookup_app.lib import readings_extractor
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
        ocra_instructor_emails = ocra.get_ocra_instructor_email_from_classid( class_id )  # probably just one email, but I don't know
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
    
    ## build data-dict ------------------------------------------
    updated_data_holder_dict = {}

    ## add basic course data to new data-holder -----------------
    basic_course_data = {
        'ocra_class_id_to_instructor_email_map_for_matches': ocra_class_id_to_instructor_email_map_for_matches,
        # 'oit_bruid_to_email_map': course_data_dict['oit_bruid_to_email_map'],
        # 'oit_course_id': course_data_dict['oit_course_id'],
        # 'oit_course_title': course_data_dict['oit_course_title'],
        'status': 'not_yet_processed',
    }
    updated_data_holder_dict[course_code] = basic_course_data
    ## switch to new data-holder --------------------------------
    course_data_dict = updated_data_holder_dict[course_code]
    ## add inverted email-match map -----------------------------
    existing_classid_to_email_map = course_data_dict['ocra_class_id_to_instructor_email_map_for_matches']
    inverted_ocra_classid_email_map = ocra.make_inverted_ocra_classid_email_map( existing_classid_to_email_map )
    course_data_dict['inverted_ocra_classid_email_map'] = inverted_ocra_classid_email_map
    log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
    ## get class_ids --------------------------------------------
    relevant_course_classids = inverted_ocra_classid_email_map.values()
    log.debug( f'relevant_course_classids, ``{pprint.pformat(relevant_course_classids)}``' )

    ## process relevant class_ids ------------------------------------
    all_course_results = {}
    for class_id in relevant_course_classids:
        ## ------------------------------------------------------
        ## GET OCRA DATA ----------------------------------------
        ## ------------------------------------------------------            
        ## ocra book data -------------------------------------------
        book_results: list = readings_extractor.get_book_readings( class_id )
        if book_results:
            for book_result in book_results:
                if book_result['bk_updated']:
                    book_result['bk_updated'] = book_result['bk_updated'].isoformat()
                if book_result['request_date']:
                    book_result['request_date'] = book_result['request_date'].isoformat()
                if book_result['needed_by']:
                    book_result['needed_by'] = book_result['needed_by'].isoformat()
                if book_result['date_printed']:
                    book_result['date_printed'] = book_result['date_printed'].isoformat()
        ## ocra all-artcles data ------------------------------------
        all_articles_results: list = readings_extractor.get_all_articles_readings( class_id )
        ## ocra filtered article data -------------------------------
        filtered_articles_results: dict = ocra.filter_article_table_results(all_articles_results)
        for type_key, result_value in filtered_articles_results.items():
            if result_value:
                for result in result_value:
                    if result['art_updated']:
                        result['art_updated'] = result['art_updated'].isoformat()
                    if result['date']:
                        result['date'] = result['date'].isoformat()
                    if result['date_due']:
                        result['date_due'] = result['date_due'].isoformat()
                    if result['request_date']:
                        result['request_date'] = result['request_date'].isoformat()
                    if result['date_printed']:
                        result['date_printed'] = result['date_printed'].isoformat()
        article_results = filtered_articles_results['article_results']
        audio_results = filtered_articles_results['audio_results']          # from article-table; TODO rename
        ebook_results = filtered_articles_results['ebook_results'] 
        excerpt_results = filtered_articles_results['excerpt_results']
        video_results = filtered_articles_results['video_results']          
        website_results = filtered_articles_results['website_results']      
        # log.debug( f'website_results, ``{pprint.pformat(website_results)}``' )
        ## ocra tracks data -----------------------------------------
        tracks_results: list = readings_extractor.get_tracks_data( class_id )   
        if tracks_results:
            for result in tracks_results:
                if result['procdate']:
                    result['procdate'] = result['procdate'].isoformat()
                if result['timing']:
                    result['timing'] = str( result['timing'] )  # i.e., converts datetime.timedelta(seconds=17) to '0:00:17'
                else:
                    result['timing'] = ''
        ## combine results ------------------------------------------
        classid_results = {
            'book_results': book_results,
            'article_results': article_results,
            'audio_results': audio_results,
            'ebook_results': ebook_results,
            'excerpt_results': excerpt_results,
            'video_results': video_results,
            'website_results': website_results,
            'tracks_results': tracks_results,
        }
        all_course_results[class_id] = classid_results

        ## end for class_id in relevant_course_classids loop...

    course_data_dict['ocra_course_data'] = all_course_results
    ocra_data_found_check = ocra.check_for_ocra_data( all_course_results )
    if ocra_data_found_check == False:
        # meta['courses_with_no_ocra_data'].append( course_code )
        pass
    course_data_dict['status'] = 'processed'

    log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )

    ## end for-course loop...


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