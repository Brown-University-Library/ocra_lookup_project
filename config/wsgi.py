"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/

---

Virtual-environment and env-var notes... ----------------------------

This file handles all three deployment scenarios: Server, Localdev using a virtual-environment, and Localdev using Docker.

Server...
    - Virtual-environment: 
        - The project's httpd/passenger.conf section allows specification of the python-path via `PassengerPython`, which auto-activates it.
        - Example `<Location /project_root>` entry: `PassengerPython /path/to/env/bin/python3`
    - Env-vars:
        - The project's httpd/passenger.conf section allows specification of the env-vars via `SenEnv`, which specifies the path to the env_settings.sh file.
        - Example `<Location /project_root>` entry: `SetEnv PREFIX__ENV_SETTINGS_PATH /path/to/project_env_settings.sh`
        - This file uses that env-var to load the `project_env_settings.sh` envar settings.
        - Passenger is able to find this file via three other `<Location /project_root>` entries:
            - `PassengerAppType wsgi` specifies the app-type
            - `PassengerAppRoot /path/to/project/config` specifies the config-directory
            - `PassengerStartupFile wsgi.py` specifies this startup file

Localdev using a virtual-environment and `python ./manage.py runserver`...
    - Virtual-environment:
        - Activated by manually by cd-ing into the project-directory, and running `source ../env/bin/activate`
    - Env-vars:
        - Activated by running, from within the project-directory, `source /path/to/project_env_settings.sh` (or sometimes that line is added to the venv's `activate` file)

Localdev using `docker-compose up`...
    - Virtual-environment: not applicable; the Dockerfile pip-installs the requirements right into the container's python-environment.
    - Env-vars:
        - The docker-compose.yml file has an `environment` setting and an `env_file` setting.
        - I don't understand the interplay between the two, but from testing, both need to be set accurately.

"""

import os, pprint, sys
import shellvars
from django.core.wsgi import get_wsgi_application

# print( 'the initial env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

PROJECT_DIR_PATH = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) )  # the parent of the config directory is the project directory
ENV_SETTINGS_FILE = os.environ['OCRA_LKP__ENV_SETTINGS_PATH']

## update path
sys.path.append( PROJECT_DIR_PATH )

## reference django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'  # so django can access its settings

## load up env vars
var_dct = shellvars.get_vars( ENV_SETTINGS_FILE )
for ( key, val ) in var_dct.items():
    os.environ[key.decode('utf-8')] = val.decode('utf-8')

# print( 'the final env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

## gogogo
application = get_wsgi_application()
