import datetime, logging

from django.conf import settings

log = logging.getLogger(__name__)


def rebuild_pdf_data_if_necessary( days: dict ) -> dict:
    """ Initiates OCRA pdf-data extraction if necessary. 
        Called by build_reading_list.manage_build_reading_list() """
    log.debug( f'days, ``{days}``' )
    num_days: int = days['days']
    return_val = {}
    # PDF_JSON_PATH: str = os.environ['LGNT__PDF_JSON_PATH']
    PDF_JSON_PATH = settings.PDF_JSON_PATH
    log.debug( f'PDF_JSON_PATH, ``{PDF_JSON_PATH}``' )
    update: bool = determine_update( num_days, PDF_JSON_PATH, datetime.datetime.now()  )
    if update:
        log.debug( 'gonna update the pdf-data -- TODO' )
        try:
            from lib import make_pdf_json_data  # the import actually runs the code
        except Exception as e:
            log.exception( 'problem running pdf-json script' )
            return_val = { 'err': repr(e) }
    else:
        log.debug( 'pdf_data is new enough; not updating' )
    return return_val


def determine_update( days: int, fpath: str, now_time: datetime.datetime ) -> bool:
    """ Determines whether to update given file. 
        Called by rebuild_pdf_data_if_necessary() """
    log.debug( f'days, ``{days}``' )
    log.debug( f'now_time, ``{now_time}``' )
    return_val = False
    last_updated_epoch_timestamp: float = pathlib.Path( fpath ).stat().st_mtime
    dt_last_updated: datetime.datetime = datetime.datetime.fromtimestamp( last_updated_epoch_timestamp )
    cutoff_date: datetime.datetime = dt_last_updated + datetime.timedelta( days )
    log.debug( f'cutoff_date, ``{str(cutoff_date)}``' )
    if cutoff_date < now_time:
        return_val = True
    log.debug( f'return_val, ``{return_val}``' )
    return return_val
