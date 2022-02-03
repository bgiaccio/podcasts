import html
import logging
import time
from datetime import timedelta

import argparse
from flask import Flask, send_from_directory, request, g
from markupsafe import escape

from podcast_server.podcastService import PodcastService

# define the app
app = Flask(__name__)

# Disable the default per request logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.before_request
def start_timer():
    g.start = time.time()


@app.after_request
def after_request(response):
    if '/health' not in request.path:
        # See https://werkzeug.palletsprojects.com/en/0.15.x/wrappers/#werkzeug.wrappers.Request
        now = time.time()
        duration = round(now - g.start, 2)
        app.logger.info(
            f"{request.remote_addr} {request.method} {request.full_path.rstrip('?')} {response.status} "
            f"{str(timedelta(seconds=duration))}")
    return response


@app.route('/feeds/<path:feedName>/rss')
def feed(feedName):
    return podcast_service.generate_podcast(escape(feedName))


@app.route('/<path:filename>', methods=['GET', 'HEAD'])
def download(filename):
    return send_from_directory(directory=podcast_service.search_dir, path=html.unescape(filename).replace('+', ' '))


if __name__ == "__main__":
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Setup podcast service')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--external', required=True, help='what the outside world will connect to us as')
    required.add_argument('--port', required=True, help='port to run the service')
    required.add_argument('--directory', required=True,
                          help='root directory of podcasts, each sub-directory will be a feed')
    args = parser.parse_args()
    app.logger.info(f'Serving podcasts on {args.external}')

    podcast_service = PodcastService(args.external, args.directory)
    app.run(host='0.0.0.0', port=args.port, debug=True)
