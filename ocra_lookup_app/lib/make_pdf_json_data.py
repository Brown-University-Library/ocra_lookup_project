"""
Queries the reserves database for past PDF file-data.
Original script could be run as stand-alone file, or is also called by loaders.rebuild_pdf_data_if_necessary()
TODO: update to be able to run stand-alone again.
"""

import datetime, json, logging, os, pprint

import pymysql
# from lib import db_stuff
from ocra_lookup_app.lib.query_ocra import DbStuff


PDF_SQL: str = os.environ['LGNT__PDF_SQL']
PDF_JSON_PATH: str = os.environ['LGNT__PDF_JSON_PATH']
# LOG_PATH: str = os.environ['LGNT__LOG_PATH']

# logging.basicConfig(
#     filename=LOG_PATH,
#     level=logging.DEBUG,
#     format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
#     datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )

db_stuff = DbStuff()

## get db connection ------------------------------------------------
db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format

## run query --------------------------------------------------------
start_time = datetime.datetime.now()
result_set: list = []
with db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor.execute( PDF_SQL )
        result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
        assert type(result_set) == list
record: dict = result_set[0]
assert type(record) == dict
log.debug( f'record, ``{record}``' )
log.debug( f'result_set, ``{pprint.pformat(result_set[0:5])}``' )
end_time = datetime.datetime.now()
elapsed: str = str( end_time - start_time )
log.debug( f'query took, ``{elapsed}``' )

## parse results ----------------------------------------------------

#   {
#     "articleid": 8,
#     "atitle": "Madison Lecture: Our Democratic Constitution",
#     "filename": "breyer_madison_lecture.pdf",
#     "pdfid": 33,
#     "requestid": "20031210153909",
#     "title": "New York Univerity Law Review"
#   },

pdf_data: dict = {}
for entry in result_set:
    result: dict = entry
    rqst_id = result.get( 'requestid', '' )
    if rqst_id:
        key = result['requestid']
        val = {
            'articleid': result.get( 'articleid', '' ),
            'atitle': result.get( 'atitle', '' ),
            'filename': result.get( 'filename', '' ),
            'pdfid': result.get( 'pdfid', '' ),
            'title': result.get( 'title', '' )
        }
        pdf_data[key] = val 

## save data --------------------------------------------------------
# jsn: str = json.dumps( result_set, sort_keys=True, indent=2 )
jsn: str = json.dumps( pdf_data, sort_keys=True, indent=2 )
log.debug( f'type(jsn), ``{type(jsn)}``' )
with open( PDF_JSON_PATH, 'w' ) as f_writer:
    f_writer.write( jsn )

## EOF