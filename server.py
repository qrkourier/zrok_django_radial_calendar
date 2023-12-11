import os
import sys

import openziti
from waitress import serve

from zrok_django_radial_calendar.wsgi import application

bind_opts = {}  # populated in main


@openziti.zitify(bindings={':8002': bind_opts})
def runServer():
    serve(application, port='8002')


if __name__ == '__main__':
    bind_opts['ztx'] = sys.argv[1]
    bind_opts['service'] = os.environ['ZROK_TOKEN']
    runServer()
