import json
import os
import sys
import time

import openziti
from waitress import serve

from zrok_django_radial_calendar.wsgi import application


# this script waits for the deployment to enable a zrok environment which produces a reserved.json file describing the
# zrok reserved share. From that file, we extract the zrok frontend endpoint and the share name (token). The frontend
# endpoint is exported to the process environment to be consumed by settings.py when configuring allowed HTTP origins.
# The token is the name of Ziti Service we need to bind, so that's passed to the ziti SDK as a bind option.

# ziti options
bind_opts = {}


def waitForEnable():
    start_time = time.time()
    while time.time() - start_time < 60:
        if os.path.exists(f'{ZROK_HOME}/.zrok/reserved.json'):
            with open(f'{ZROK_HOME}/.zrok/reserved.json') as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    time.sleep(1)
                    continue
                if 'frontend_endpoints' in data and data['frontend_endpoints']:
                    zrok_frontend = data['frontend_endpoints'][0]
                    bind_opts['service'] = data['token']
                    zrok_frontend = zrok_frontend.replace('https://', '')
                    if zrok_frontend.endswith('/'):
                        zrok_frontend = zrok_frontend[:-1]
                    os.environ['ZROK_FRONTEND'] = zrok_frontend
                    break
        else:
            time.sleep(1)
    else:  # executed if the loop ended normally (no break)
        raise Exception('Timeout: Unable to find reserved.json within 60 seconds')
    print(f'INFO: ZROK_FRONTEND is https://{zrok_frontend}/')


# the port is fictitious because we're using ziti to bind to the service, so there are no listening ports. waitress
# requires a port, so we're using the port number only to integrate the ziti SDK with waitress.
@openziti.zitify(bindings={':8002': bind_opts})
def runServer():
    serve(application, port='8002')


if __name__ == '__main__':
    # the filesystem path to zrok enable's HOME directory
    ZROK_HOME = sys.argv[1]  # /mnt
    # this is the standard location for the ziti identity file created by zrok enable
    bind_opts['ztx'] = f"{ZROK_HOME}/.zrok/identities/environment.json"

    waitForEnable()
    runServer()
