import datetime, json, logging, pprint

import trio
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from ocra_lookup_app.lib import find_view_helper
from ocra_lookup_app.lib import version_helper
from ocra_lookup_app.lib.version_helper import GatherCommitAndBranchData

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------


def info(request):
    return HttpResponse( 'info coming' )


@ensure_csrf_cookie
def find(request):
    log.debug( 'starting find()' )
    context = find_view_helper.make_context( request )
    log.debug( f'context, ``{context}``' )
    return render( request, 'find.html', context )


def form_handler(request):
    log.debug( 'starting form_handler()' )
    log.debug( f'request.POST, ``{pprint.pformat(request.POST)}``' )
    return HttpResponse( 'form-handler coming' )
    # return HttpResponseRedirect( reverse('results_url') )

def results(request):
    return HttpResponse( 'results coming' )


# -------------------------------------------------------------------
# support urls
# -------------------------------------------------------------------


def error_check( request ):
    """ For an easy way to check that admins receive error-emails (in development)...
        To view error-emails in runserver-development:
        - run, in another terminal window: `python -m smtpd -n -c DebuggingServer localhost:1026`,
        - (or substitue your own settings for localhost:1026)
    """
    log.debug( 'starting error_check()' )
    log.debug( f'project_settings.DEBUG, ``{project_settings.DEBUG}``' )
    if project_settings.DEBUG == True:
        log.debug( 'triggering exception' )
        raise Exception( 'Raising intentional exception.' )
    else:
        log.debug( 'returing 404' )
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )


def version( request ):
    """ Returns basic branch and commit data. """
    log.debug( 'starting version()' )
    rq_now = datetime.datetime.now()
    gatherer = GatherCommitAndBranchData()
    trio.run( gatherer.manage_git_calls )
    commit = gatherer.commit
    branch = gatherer.branch
    info_txt = commit.replace( 'commit', branch )
    context = version_helper.make_context( request, rq_now, info_txt )
    output = json.dumps( context, sort_keys=True, indent=2 )
    log.debug( f'output, ``{output}``' )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def root( request ):
    return HttpResponseRedirect( reverse('info_url') )


# -------------------------------------------------------------------
# htmx experimentation urls
# -------------------------------------------------------------------


@ensure_csrf_cookie
def htmx_example(request):
    """ From: <https://www.sitepoint.com/htmx-introduction/> """
    return render( request, 'htmx_example.html' )


def htmx_f__new_content(request):
    """ Serves out content for htmx_example.html, specifically for 
    - ``example 5: new-content fade-in (of fragment)`` 
    - ``example 6: form-validation (client-side-only)``
    """
    html = '''
<div id="example_5_content" class="fadeIn">
    New Content New Content New Content 
</div>
'''
    return HttpResponse( html )


def htmx_f__email_validator(request):
    """ Serves out content for `example 7: form-validation (server-side)`, 
        specifically for email-validator response. """
    log.debug( f'request.POST, ``{pprint.pformat(request.POST)}``' )
    html = '<p>email-validator response</p>'
    return HttpResponse( html )


def htmx_f__form_handler(request):
    """ Serves out content for `example 7: form-validation (server-side)`, 
        specifically for submit-form response. """
    log.debug( f'request.POST, ``{pprint.pformat(request.POST)}``' )
    email_data = request.POST.get( 'email', '' )
    if email_data == '':
        html = '''<p>email cannot be empty.</p>'''
        return HttpResponse( html )
    else:
        return HttpResponseRedirect( reverse('htmx_results_url') )


def htmx_results(request):
    return HttpResponse( 'htmx-experiment results coming' )
