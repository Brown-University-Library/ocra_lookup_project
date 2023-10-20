import datetime, json, logging, pprint

import trio
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from ocra_lookup_app.lib import find_view_helper
from ocra_lookup_app.lib import version_helper
from ocra_lookup_app.lib.version_helper import GatherCommitAndBranchData
from .forms import CourseAndEmailForm

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
            url = '%s?course_code=%s' % ( reverse('results_url'), request.POST['course_code'] )
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


# def form_handler(request):
#     """ Handles POST from find-form. """
#     log.debug( 'starting form_handler()' )
#     log.debug( f'request, ``{pprint.pformat(request)}``' )
#     ## clear out session error text ---------------------------------
#     log.debug( f'request.session.items(), ``{pprint.pformat(request.session.items())}``' )
#     request.session['session_error_message'] = ''
#     ## examine POST -------------------------------------------------
#     try:
#         if request.method != 'POST':
#             log.debug( 'non-POST detected; returning bad-request' )
#             return HttpResponseBadRequest( '400 / Bad Request' )
#         log.debug( 'POST detected' )
#         log.debug( f'request.POST, ``{pprint.pformat(request.POST)}``' )
#         ## handle form ------------------------------------------
#         log.debug( 'about to instantiate form' )
#         # form = UploadFileForm(request.POST, request.FILES)
#         form = CourseAndEmailForm( request.POST )
#         log.debug( f'form.__dict__, ``{pprint.pformat(form.__dict__)}``' )
#         if form.is_valid():
#             log.debug( 'form is valid' )
#             log.debug( f'form.cleaned_data, ``{pprint.pformat(form.cleaned_data)}``' )
#             log.debug( f'request.session.items(), ``{pprint.pformat(request.session.items())}``' )
#             log.debug( 'setting redirect to results' )
#             resp = HttpResponseRedirect( reverse('results_url') )  
#         else:
#             log.debug( 'form not valid' )
#             log.debug( f'form.errors, ``{pprint.pformat(form.errors)}``' )
#             errors_html: str = form.errors.as_ul()
#             log.debug( f'errors_html, ``{pprint.pformat(errors_html)}``' )
#             request.session['course_code_value'] = request.POST['course_code']      # to avoid re-entering
#             request.session['email_address_value'] = request.POST['email_address']  # to avoid re-entering
#             request.session['session_error_message'] = errors_html
#             log.debug( 'setting redirect back to find-form' )
#             resp = HttpResponseRedirect( reverse('find_url') )
#         log.debug( 'POST handled, about to redirect' )
#         log.debug( f'at end of POST; request.session.keys(), ``{pprint.pformat(request.session.keys())}``' )
#         log.debug( f'at end of POST; request.session["session_error_message"], ``{pprint.pformat(request.session["session_error_message"])}``' )
#     except Exception as e:
#         log.exception( 'problem in uploader()...' )
#         resp = HttpResponseServerError( 'Rats; webapp error. DT has been notified, but if this continues, bug them!' )
#     return resp    
#     ## end def form_handler()


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
