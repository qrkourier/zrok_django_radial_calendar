import json
import os
import sys
import time

import zrok
from waitress import serve


# this script waits for the deployment to enable a zrok environment which produces a reserved.json file describing the
# zrok reserved share. From that file, we extract the zrok frontend endpoint and the share name (token).  The token is
# the name of Ziti Service we need to bind, so that's passed to the ziti SDK as a bind option.

# make global dict so we can assign values in functions then use it in a decoration
zrok_opts = {}
# the port is fictitious because we're using ziti to bind to the service, so there are no listening ports. waitress
# requires a port, so we're using the port number only to integrate the ziti SDK with waitress.
WAITRESS_PORT = 8000


def waitForEnableAndReserve(home_dir: str):
    start_time = time.time()
    while time.time() - start_time < 60:
        if os.path.exists(f'{home_dir}/.zrok/reserved.json'):
            with open(f'{home_dir}/.zrok/reserved.json') as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    time.sleep(1)
                    continue

                if 'frontend_endpoints' in data and data['frontend_endpoints']:
                    zrok_frontend = data['frontend_endpoints'][0].replace('https://', '')
                    if zrok_frontend.endswith('/'):
                        zrok_frontend = zrok_frontend[:-1]
                    # set the ZROK_FRONTEND environment variable so that settings.py can use it to configure allowed
                    # HTTP origins
                    os.environ['ZROK_FRONTEND'] = zrok_frontend
                    print(f"INFO: ZROK_FRONTEND is https://{os.environ['ZROK_FRONTEND']}/")
                else:
                    raise Exception('Unable to find frontend_endpoints in reserved.json')

                if 'token' in data and data['token']:
                    return data['token']
                else:
                    raise Exception('Unable to find share token in reserved.json')
        else:
            time.sleep(1)
    else:  # executed if the loop ended normally (no break)
        raise Exception('Timeout: Unable to find reserved.json within 60 seconds')


def configureZrok(token: str, home_dir: str):
    os.environ['HOME'] = home_dir
    zrok_root = zrok.environment.root.Load()
    return zrok.decor.Opts(root=zrok_root, shrToken=token, bindPort=WAITRESS_PORT)


@zrok.decor.zrok(opts=zrok_opts)
def runServer():
    from zrok_django_radial_calendar.wsgi import application
    serve(application, port=WAITRESS_PORT)


if __name__ == '__main__':
    # the filesystem path to zrok enable's HOME directory
    zrok_home = sys.argv[1]  # /mnt
    share_token = waitForEnableAndReserve(zrok_home)
    zrok_opts['cfg'] = configureZrok(token=share_token, home_dir=zrok_home)
    runServer()
