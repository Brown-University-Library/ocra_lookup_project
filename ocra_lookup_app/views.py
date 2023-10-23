import datetime, json, logging, pprint

import trio
from .forms import CourseAndEmailForm
from django.conf import settings as project_settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from ocra_lookup_app.lib import find_view_helper
from ocra_lookup_app.lib import version_helper
from ocra_lookup_app.lib.version_helper import GatherCommitAndBranchData
from ocra_lookup_app.models import CourseInfo

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------


def info(request):
    return HttpResponse( 'info coming' )


@ensure_csrf_cookie
def find(request):
    """ Handles GET to find-form. """
    log.debug( 'starting find()' )
    log.debug( f'request.session.items(), ``{pprint.pformat(request.session.items())}``' )
    log.debug( f'request.session.keys(), ``{pprint.pformat(request.session.keys())}``' )
    context = {}
    if 'course_code_value' in list( request.session.keys() ):
        context['course_code_value'] = request.session['course_code_value']
    if 'email_address_value' in request.session.keys():
        context['email_address_value'] = request.session['email_address_value']
    if 'session_error_message' in request.session.keys():
        errors_html = request.session['session_error_message']
        context['errors_html'] = errors_html
    log.debug( f'context, ``{context}``' )
    request.session['course_code_value'] = ''
    request.session['email_address_value'] = ''
    request.session['session_error_message'] = ''
    log.debug( f'context, ``{context}``' )
    return render( request, 'find.html', context )


def form_handler(request):
    """ Handles POST from find-form. """
    log.debug( 'starting form_handler()' )
    request.session['session_error_message'] = ''  # session-errors set here
    try:
        if request.method != 'POST':
            log.debug( 'non-POST detected; returning bad-request' )
            return HttpResponseBadRequest( '400 / Bad Request' )
        form = CourseAndEmailForm( request.POST )
        if form.is_valid():
            ## look for an existing record --------------------------
            ci = CourseInfo.objects.filter( 
                course_code=request.POST['course_code'].lower(), 
                email_address=request.POST['email_address'].lower() ).first()
            if ci:
                log.debug( 'existing record found' )
                url = reverse( 'results_url', kwargs={'the_uuid': ci.uuid} )
            ## no existing record, so create one --------------------
            else:  
                log.debug( 'no existing record found' )
                ci = CourseInfo()
                ci.course_code = request.POST['course_code']
                ci.email_address = request.POST['email_address']
                ci.save()
                ci.refresh_from_db()
                url = reverse( 'results_url', kwargs={'the_uuid': ci.uuid} )
            log.debug( f'redirect-url, ``{url}``' )
            resp = HttpResponseRedirect( url )  
        else:
            request.session['course_code_value'] = request.POST['course_code']      # to avoid re-entering
            request.session['email_address_value'] = request.POST['email_address']  # to avoid re-entering
            request.session['session_error_message'] = form.errors.as_ul()          # for display back in find-form
            resp = HttpResponseRedirect( reverse('find_url') )
    except Exception as e:
        log.exception( 'problem in uploader()...' )
        resp = HttpResponseServerError( 'Rats; webapp error. DT has been notified, but if this continues, bug them!' )
    return resp    
    ## end def form_handler()


def results(request, the_uuid):
    """ - Checks if data is in db.
        - If necessary, querys OCRA for data (and saves it to db).
        - Prepares downloadable reading-list file.
    """
    ## use the get query for a CourseInfo.uuid ------------------
    log.debug('starting results()')
    log.debug(f'the_uuid, ``{the_uuid}``')
    try:
        ci = get_object_or_404(CourseInfo, uuid=the_uuid)
    except ValidationError:
        log.exception( 'problem in uuid-lookup...' )
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )
    log.debug( f'ci, ``{pprint.pformat(ci.__dict__)}``' )
    tmp_return_string = f'course-code, ``{ci.course_code}``; email-address, ``{ci.email_address}``'
    return HttpResponse( f'results coming for: {tmp_return_string}' )


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
