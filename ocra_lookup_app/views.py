import datetime, json, logging, os, pprint

import trio
# from .forms import CourseAndEmailForm
from django.conf import settings 
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from ocra_lookup_app.forms import CourseAndEmailForm 
from ocra_lookup_app.lib import csv_maker
from ocra_lookup_app.lib import leganto_final_processor
from ocra_lookup_app.lib import results_view_helper
from ocra_lookup_app.lib import version_helper
from ocra_lookup_app.lib.version_helper import GatherCommitAndBranchData
from ocra_lookup_app.models import CourseInfo
from uuid import UUID

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------


# def info(request):
#     return HttpResponse( 'info coming' )


@ensure_csrf_cookie
def find(request):
    """ On GET, displays form.
        On POST, processes form. """
    log.debug('starting find()')
    log.debug( f'request.method, ``{request.method}``' )
    form = 'init'
    if request.method == 'GET':
        log.debug( 'GET detected' )
        form = CourseAndEmailForm()
    elif request.method == 'POST':
        log.debug( 'POST detected' )
        form = CourseAndEmailForm( request.POST )
        log.debug( 'form instantiated' )
        if form.is_valid():
            log.debug( 'form is valid' )
            log.debug( f'form.cleaned_data, ``{form.cleaned_data}``' )
            ## look for an existing record --------------------------
            log.debug( f'searching for existing record on course_code, ``{form.cleaned_data["course_code"]}``; email_address, ``{form.cleaned_data["email_address"]}``' )
            ci = CourseInfo.objects.filter( 
                course_code=form.cleaned_data['course_code'],  # all form.cleaned_data values are stripped, and except for title, lower-cased
                email_address=form.cleaned_data['email_address']
                ).first()
            if ci:  # TODO -- refactor a bit to merge the save-code
                log.debug( 'existing record found (for course-code & instructor), will save year, term, and title' )
                ## update year/term/title ---------------------------
                ci.year = form.cleaned_data['year']
                ci.term = form.cleaned_data['term']
                ci.course_title = form.cleaned_data['course_title']
                ci.save()
                url = reverse( 'results_url', kwargs={'the_uuid': ci.uuid} )
            ## no existing record, so create one --------------------
            else:  
                log.debug( 'no existing record found, will save everything' )
                ci = CourseInfo()
                ci.course_code = form.cleaned_data['course_code']
                ci.email_address = form.cleaned_data['email_address']
                ci.year = form.cleaned_data['year']
                ci.term = form.cleaned_data['term']
                ci.course_title = form.cleaned_data['course_title']
                ci.save()
                ci.refresh_from_db()  # to get the uuid
                url = reverse( 'results_url', kwargs={'the_uuid': ci.uuid} )
            log.debug( f'redirect-url, ``{url}``' )
            return HttpResponseRedirect( url )  
        else:
            log.debug( 'form is not valid, so will return the updated form-object (which now will contain errors)' )
            log.debug( f'form.errors, ``{form.errors}``' )
    else:
        return HttpResponseBadRequest( '400 / Bad Request' )
    return render(request, 'find.html', {'form': form})


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

    ## temp display from db -------------------------------------
    # ci_dct = model_to_dict(ci)
    # ci_dct['uuid'] = str( ci.uuid )
    # log.debug( f'ci_dct from django model-to-dict, ``{pprint.pformat(ci_dct)}``' )
    # ci_dct2 = f'{pprint.pformat(ci.__dict__)}'
    # log.debug( f'ci_dct2 from a straight __dict__, ``{pprint.pformat(ci_dct2)}``' )
    # ci_jsn = json.dumps(ci_dct, sort_keys=True, indent=2)
    # return HttpResponse( ci_jsn, content_type='application/json' )

    ## check if data exists in db -----------------------------------
    ocra_data: list = []
    if ci.data:
        log.debug( 'data exists in db-cache' )
        ocra_data: list = json.loads( ci.data )
    ## if data doesn't exist in db, query OCRA ----------------------
    else:
        log.debug( 'data does not exist in db; querying OCRA' )
        ocra_data: list = results_view_helper.query_ocra( ci.course_code, ci.email_address, ci.year, ci.term, ci.course_title )
        log.debug( 'ocra queried for data' )
        if ocra_data:  # at the least it'll be an empty list
            log.debug( 'ocra data found' )
        else:
            log.debug( 'no ocra data found' )
        jsn: str = json.dumps( ocra_data )
        ci.data = jsn  # type: ignore
        ci.save()
    log.debug( f'data, ``{pprint.pformat(ocra_data)}``' )

    ## make the tsv file --------------------------------------------
    csv_maker.create_tsv( ocra_data, leganto_final_processor.get_headers(), str(ci.uuid) )

    ## prepare context ----------------------------------------------
    context = results_view_helper.make_context( request, ci.course_code, ci.email_address, ocra_data )
    context[ 'result_uuid' ] = str( ci.uuid )

    ## return response ----------------------------------------------
    if request.GET.get( 'format', '' ) == 'json':
        log.debug( 'returning json' )
        jsn = json.dumps( context, sort_keys=True, indent=2 )
        return HttpResponse( jsn, content_type='application/json; charset=utf-8' )
    else:
        log.debug( 'returning html' )
        return render( request, 'results.html', context )

    ## end def results()


# def view_tsv(request, file_uuid: UUID):
#     log.debug( 'starting view_tsv()' )
#     # Construct file path using the UUID
#     file_name = f'{file_uuid}.tsv'
#     csv_name = f'{file_uuid}.csv'
#     log.debug( f'file_name, ``{file_name}``')
#     # file_path = os.path.join(settings.BASE_DIR, 'path/to/your/files', file_name)
#     file_path = os.path.join( settings.TSV_OUTPUT_DIR_PATH, file_name )
#     log.debug( f'file_path, ``{file_path}``' )

#     if not os.path.exists(file_path):
#         return HttpResponseNotFound('File not found')

#     # Serve the file inline
#     response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
#     response['Content-Disposition'] = f'inline; filename="{csv_name}"'
#     return response


def view_tsv(request, file_uuid: UUID):
    log.debug( 'starting view_tsv()' )
    # Construct file path using the UUID
    file_name = f'{file_uuid}.tsv'
    log.debug( f'file_name, ``{file_name}``')
    # file_path = os.path.join(settings.BASE_DIR, 'path/to/your/files', file_name)
    file_path = os.path.join( settings.TSV_OUTPUT_DIR_PATH, file_name )
    log.debug( f'file_path, ``{file_path}``' )

    if not os.path.exists(file_path):
        return HttpResponseNotFound('File not found')

    # Serve the file inline
    response = FileResponse( open(file_path, 'rb'), content_type='text/tab-separated-values' )
    response['Content-Disposition'] = f'inline; filename="{file_name}"'
    return response


def download_tsv(request, file_uuid: UUID):
    log.debug( 'starting download_tsv()' )
    # Construct file path using the UUID
    file_name = f'{file_uuid}.tsv'
    log.debug( f'file_name, ``{file_name}``')
    # file_path = os.path.join(settings.BASE_DIR, 'path/to/your/files', file_name)
    file_path = os.path.join( settings.TSV_OUTPUT_DIR_PATH, file_name )
    log.debug( f'file_path, ``{file_path}``' )

    if not os.path.exists(file_path):
        return HttpResponseNotFound('File not found')

    # Serve the file as an attachment, prompting a download
    response = FileResponse( open(file_path, 'rb'), as_attachment=True, content_type='text/tab-separated-values' )
    return response

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
    log.debug( f'settings.DEBUG, ``{settings.DEBUG}``' )
    if settings.DEBUG == True:
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
    return HttpResponseRedirect( reverse('find_url') )


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
