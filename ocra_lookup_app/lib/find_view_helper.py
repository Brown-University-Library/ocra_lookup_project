from ocra_lookup_app.lib import common

def make_context( request: str ) -> dict:
    pattern_header_html: str = common.prep_pattern_header_html()
    return {}