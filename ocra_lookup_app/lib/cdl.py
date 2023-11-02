import logging, os, pprint

from fuzzywuzzy import fuzz
# from lib import db_stuff
from ocra_lookup_app.lib.query_ocra import DbStuff

db_stuff = DbStuff()


# LOG_PATH: str = os.environ['LGNT__LOG_PATH']
# logging.basicConfig(
#     filename=LOG_PATH,
#     level=logging.DEBUG,
#     format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
#     datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


class CDL_Checker(object):

    def __init__( self ):
        self.CDL_TITLES: list = []

    def populate_cdl_titles( self ) -> list:
        log.debug( 'starting populate_cdl_titles()' )
        db_connection = db_stuff.get_CDL_db_connection()
        sql = "SELECT * FROM `cdl_app_item` ORDER BY `title` ASC"
        log.debug( f'sql, ``{sql}``' )
        result_set: list = []
        with db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor.execute( sql )
                result_set = list( db_cursor.fetchall() )
                assert type(result_set) == list
        return result_set


    def search_cdl( self, search_title: str ) -> list:
        """ Fuzzy-searches cdl-titles, returns back score and file_name. """
        log.debug( f'search_title, ``{search_title}``' )
        assert type(search_title) == str
        matches = []
        if len( search_title.strip() ) > 0:
            if self.CDL_TITLES == []:
                log.debug( 'populating CDL_TITLES' )
                self.CDL_TITLES = self.populate_cdl_titles()
                # log.debug( f'CDL_TITLES, ``{pprint.pformat(CDL_TITLES)}``' )
                log.debug( f'len(self.CDL_TITLES), ``{len(self.CDL_TITLES)}``' )
            for entry in self.CDL_TITLES:
                assert type(entry) == dict
                score: int = fuzz.ratio( search_title, entry['title'] )
                if score > 80:
                    entry['fuzzy_score'] = score
                    matches.append( entry )
        log.debug( f'matches, ``{pprint.pformat(matches)}``' )
        return matches

    def prep_cdl_field_text( self, entries: list ) -> str:
        result = 'no CDL link found'
        if len( entries ) == 1:
            entry = entries[0]
            if entry['fuzzy_score'] > 97:
                result = f'CDL link likely: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
            else:
                result = f'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
        elif len( entries ) > 1:
            result: str = f'Multiple possible CDL links: '
            cdl_pattern: str = '<https://cdl.library.brown.edu/cdl/item/ITEM_ID>'
            for ( i, entry ) in enumerate( entries ):
                if i == 0:
                    append_str = cdl_pattern.replace( 'ITEM_ID', entry['item_id'] )
                else:
                    temp_str = cdl_pattern.replace( 'ITEM_ID', entry['item_id'] )
                    append_str = f', {temp_str}'
                result = result + append_str
        log.debug( f'result, ``{result}``' )
        return result

    ## end class CDL_Checker()


def run_article_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Sees if data contains a CDL reference, and, if so, see if I can find one.
        Called by and map_article(). 
        TODO -- since this now does the same thing as run_book_cdl_check(), refactor. """
    log.debug( f'type(ocra_facnotes_data), ``{type(ocra_facnotes_data)}``' )
    log.debug( f'ocra_facnotes_data for article cdl check, ``{ocra_facnotes_data}``' )
    log.debug(f'ocra_title, ``{ocra_title}``')
    field_text = 'no cdl link found'
    results: list = cdl_checker.search_cdl( ocra_title )
    field_text: str = cdl_checker.prep_cdl_field_text( results )
    log.debug( f'article cdl lookup, ``{field_text}``' )
    return field_text


def run_book_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Try CDL check on ocra-title.
        (The `ocra_facnotes_data` string is not used and deprecated.)
        Called by map_book(). """
    log.debug( f'type(ocra_facnotes_data), ``{type(ocra_facnotes_data)}``' )
    log.debug( f'ocra_facnotes_data, ``{ocra_facnotes_data}``' )
    if ocra_title == None:
        ocra_title = ''
    field_text: str = ocra_facnotes_data
    results: list = cdl_checker.search_cdl( ocra_title )
    field_text: str = cdl_checker.prep_cdl_field_text( results )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text


def run_ebook_cdl_check( ocra_facnotes_data: str, ocra_art_url: str, ocra_title: str, cdl_checker  ) -> str:
    """ If ocra_art_url has a cdl link, use that.
        Otherwise, try CDL check on ocra-title.
        (The `ocra_facnotes_data` string is not used and deprecated.)
        Called by map_book(). """
    log.debug( f'ocra_facnotes_data, ``{ocra_facnotes_data}``' )
    log.debug( f'ocra_art_url, ``{ocra_art_url}``' )
    log.debug( f'ocra_title, ``{ocra_title}``' )
    if ocra_art_url == None:
        ocra_art_url = ''
    if ocra_title == None:
        ocra_title = ''
    field_text: str = 'no CDL link found'
    if 'cdl.library.brown.edu' in ocra_art_url:
        field_text = f'CDL link likely: {ocra_art_url}'
    else:
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text
