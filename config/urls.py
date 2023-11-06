from django.contrib import admin
from django.urls import path
from ocra_lookup_app import views


urlpatterns = [
    ## main ---------------------------------------------------------
    path( 'info/', views.info, name='info_url' ),
    path( 'find/', views.find, name='find_url' ),
    # path( 'form_handler/', views.form_handler, name='form_handler_url' ),
    # path( 'results/', views.results, name='results_url' ),
    path( 'results/<the_uuid>/', views.results, name='results_url' ),

    path('view_tsv/<uuid:file_uuid>/', views.view_tsv, name='view_tsv'),
    path('download_tsv/<uuid:file_uuid>/', views.download_tsv, name='download_tsv'),

    ## other --------------------------------------------------------
    path( '', views.root, name='root_url' ),
    path( 'admin/', admin.site.urls ),
    path( 'error_check/', views.error_check, name='error_check_url' ),
    path( 'version/', views.version, name='version_url' ),

    ## htmx experimentation -----------------------------------------
    path( 'htmx_example/', views.htmx_example, name='htmx_example_url' ),
    path( 'htmx_f__new_content/', views.htmx_f__new_content, name='htmx_f__new_content_url' ),
    path( 'htmx_f__email_validator/', views.htmx_f__email_validator, name='htmx_f__email_validator_url' ),
    path( 'htmx_f__form_handler/', views.htmx_f__form_handler, name='htmx_f__form_handler_url' ),
    path( 'htmx_results/', views.htmx_results, name='htmx_results_url' ),

]
