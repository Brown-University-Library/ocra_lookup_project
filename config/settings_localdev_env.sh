#!/bin/bash


## LOCALDEV settings for django `x_project`
##
## This file is loaded by `env/bin/activate` when running locally...
## ...and by `project/config/passenger_wsgi.py` on our servers.
##
## When deploying on our servers, copy this file to the appropriate place, edit it, 
## ...and point to it from activate and the apache <Location> entry.


## ============================================================================
## standard project-level settings
## ============================================================================

export XPRJCT_42__SECRET_KEY="example_secret_key"

export XPRJCT_42__DEBUG_JSON="true"

export XPRJCT_42__ADMINS_JSON='
    [
      [
        "exampleFirst exampleLast",
        "example@domain.edu"
      ]
    ]
    '

export XPRJCT_42__ALLOWED_HOSTS_JSON='["127.0.0.1", "127.0.0.1:8000", "0.0.0.0:8000", "localhost:8000"]'  # must be json

export XPRJCT_42__DATABASES_JSON='
    {
      "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "HOST": "",
        "NAME": "../DB/x_project.sqlite3",
        "PASSWORD": "",
        "PORT": "",
        "USER": ""
      }
    }
    '

export XPRJCT_42__STATIC_URL="/static/"
export XPRJCT_42__STATIC_ROOT="/static/"

export XPRJCT_42__EMAIL_HOST="localhost"
export XPRJCT_42__EMAIL_PORT="1026"  # will be converted to int in settings.py
export XPRJCT_42__SERVER_EMAIL="donotreply_x-project@domain.edu"

export XPRJCT_42__LOG_PATH="../logs/x_project.log"
export XPRJCT_42__LOG_LEVEL="DEBUG"

export XPRJCT_42__CSRF_TRUSTED_ORIGINS_JSON='["localhost", "127.0.0.1"]'

## https://docs.djangoproject.com/en/3.2/topics/cache/
## - TIMEOUT is in seconds (0 means don't cache); CULL_FREQUENCY defaults to one-third
export XPRJCT_42__CACHES_JSON='
{
  "default": {
    "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
    "LOCATION": "../cache_dir",
    "TIMEOUT": 0,
    "OPTIONS": {
        "MAX_ENTRIES": 1000
    }
  }
}
'

## ============================================================================
## app
## ============================================================================

export XPRJCT_42__README_URL="https://github.com/birkin/django_template_32_project/blob/main/README.md"

## auth -------------------------------------------------------------

export XPRJCT_42__SUPER_USERS_JSON='[
]'

export XPRJCT_42__STAFF_USERS_JSON='
[
  "eppn@domain.edu"
]'

export XPRJCT_42__STAFF_GROUPER_GROUP="the:group"

export XPRJCT_42__TEST_META_DCT_JSON='{
  "Shibboleth-eppn": "eppn@brown.edu",
  "Shibboleth-brownNetId": "First_Last",
  "Shibboleth-mail": "first_last@domain.edu",
  "Shibboleth-givenName": "First",
  "Shibboleth-sn": "Last",
  "Shibboleth-isMemberOf": "aa:bb:cc;dd:ee:ff;the:group;gg:hh"
}'

export XPRJCT_42__LOGIN_PROBLEM_EMAIL="x_project_problems@domain.edu"


## end --------------------------------------------------------------
