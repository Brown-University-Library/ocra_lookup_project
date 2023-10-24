import logging, os

# from lib import db_stuff
from ocra_lookup_app.lib.query_ocra import DbStuff

log = logging.getLogger(__name__)

db_stuff = DbStuff()


def get_book_readings( class_id: str ) -> list:
    db_connection = db_stuff.get_db_connection()
    sql = f"SELECT * FROM reserves.books, reserves.requests WHERE books.requestid = requests.requestid AND classid = {int(class_id)} ORDER BY `books`.`bk_title` ASC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\nbooks\n----------' )
    for entry in result_set:
        log.debug( f'\n\nbook, ``{entry}``')
    log.debug( '\n\n----------' )
    return result_set


def get_all_articles_readings( class_id: str ) -> list:
    """ Runs sql to get article-data for given class_id. 
        Previously checked for `format = 'article'`, but now ignores that; formats are filtered later.
        Called by build_reading_list.prep_basic_data() """
    db_connection = db_stuff.get_db_connection()
    sql = f"SELECT * FROM reserves.articles, reserves.requests WHERE articles.requestid = requests.requestid AND classid = {int(class_id)} AND articles.requestid = requests.requestid AND articles.status != 'volume on reserve' AND articles.status != 'purchase requested' ORDER BY `articles`.`atitle` ASC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\narticles\n----------' )
    for entry in result_set:
        log.debug( f'\n\narticle, ``{entry}``')
        if entry['doi']:
            if entry['doi'][0:1] == ' ':
                log.debug( 'cleaning doi' )
                entry['doi'] = entry['doi'].strip()
        else:
            log.debug( 'setting `None` doi to ""' )
            entry['doi']
    log.debug( '\n\n----------' )
    return result_set


def get_excerpt_readings( class_id: str ) -> list:
    db_connection = db_stuff.get_db_connection()
    sql = f"SELECT * FROM reserves.articles, reserves.requests WHERE requests.classid = {int(class_id)} AND format = 'excerpt' AND articles.requestid = requests.requestid AND articles.status != 'volume on reserve' AND articles.status != 'purchase requested' ORDER BY `articles`.`atitle` ASC;"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\nexcerpts\n----------' )
    for entry in result_set:
        log.debug( f'\n\nexcerpt, ``{entry}``')
    log.debug( '\n\n----------' )
    return result_set
    

def get_tracks_data( class_id: str ) -> list:
    db_connection = db_stuff.get_db_connection()
    sql = f"SELECT * FROM reserves.tracks, reserves.tracks2classes WHERE tracks.trackid = tracks2classes.trackid AND tracks2classes.classid = {int(class_id)} ORDER BY `tracks`.`tracktitle` ASC;"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\ntracks\n----------' )
    for entry in result_set:
        log.debug( f'\n\ntrack, ``{entry}``')
    log.debug( '\n\n----------' )
    return result_set
