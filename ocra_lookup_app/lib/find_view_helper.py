import logging

from ocra_lookup_app.lib import common

log = logging.getLogger(__name__)


def make_context( request: str ) -> dict:
    pattern_header_html: str = common.prep_pattern_header_html()
    context = {
        'pattern_header': pattern_header_html,
    }
    log.debug( f'context keys, ``{context.keys()}``' )
    return context