import csv, datetime, logging, os, pprint
from django.conf import settings

log = logging.getLogger(__name__)


# CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']


def create_csv( data: list, headers: list ) -> None:
    """ Credit: <https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#writing-from-a-dictionary> """

    log.debug( f'data, ``{pprint.pformat(data)}``' )
    log.debug( f'headers, ``{pprint.pformat(headers)}``' )

    cleaned_data: list = []
    for entry in data:
        entry: dict = entry
        # if 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND' in entry['reading_list_library_note']:
        if 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND' in entry['citation_library_note']:
            pass
        else:
            cleaned_data.append( entry )
    
    # output_filename: str = f'reading_list_{datetime.datetime.now().isoformat()}.csv'.replace( ':', '-' )  # produces, eg, `reading_list_2022-09-06T10-59-04.345469.csv`
    # output_filename: str = f'list_{datetime.datetime.now().isoformat()}.tsv'.replace( ':', '-' )[:22]  # produces, eg, `reading_list_2022-09-06T10-59-04.34.tsv`
    datetimestamp: str = datetime.datetime.now().isoformat().replace( ':', '-' )[:22]
    output_filename: str = f'list_{datetimestamp}.tsv'  # produces, eg, `reading_list_2022-09-06T10-59-04.34.tsv`
    log.debug( f'output_filename, ``{output_filename}``' ) 

    output_filepath: str = f'{CSV_OUTPUT_DIR_PATH}/2023_fall/{output_filename}'

    ## open a new file for writing - if file exists, contents will be erased
    csvfile = open( output_filepath, 'w' )

    ## make a new variable - c - for Python's DictWriter object - note that fieldnames is required
    # c = csv.DictWriter( csvfile, fieldnames=headers) 

    ## make a DictWriter with a tab delimiter
    c = csv.DictWriter( csvfile, fieldnames=headers, delimiter='\t' )

    ## optional - write a header row
    c.writeheader()

    ## write all rows from list to file
    # c.writerows( cleaned_data )
    c.writerows( cleaned_data )

    # save and close file
    csvfile.close()

    return

# def create_csv( data: list, headers: list ) -> None:
#     """ Credit: <https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#writing-from-a-dictionary> """

#     log.debug( f'data, ``{pprint.pformat(data)}``' )
#     log.debug( f'headers, ``{pprint.pformat(headers)}``' )

#     cleaned_data: list = []
#     for entry in data:
#         entry: dict = entry
#         if 'NO-OCRA-DATA-FOUND' in entry['section_id']:
#             pass
#         else:
#             cleaned_data.append( entry )
    
#     output_filename: str = f'reading_list_{datetime.datetime.now().isoformat()}.csv'.replace( ':', '-' )  # produces, eg, `reading_list_2022-09-06T10-59-04.345469`
#     log.debug( f'output_filename, ``{output_filename}``' ) 

#     output_filepath: str = f'{CSV_OUTPUT_DIR_PATH}/{output_filename}'

#     ## open a new file for writing - if file exists, contents will be erased
#     csvfile = open( output_filepath, 'w' )

#     ## make a new variable - c - for Python's DictWriter object - note that fieldnames is required
#     c = csv.DictWriter( csvfile, fieldnames=headers) 

#     ## optional - write a header row
#     c.writeheader()

#     ## write all rows from list to file
#     c.writerows( cleaned_data )

#     # save and close file
#     csvfile.close()

#     return