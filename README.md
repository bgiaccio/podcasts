# Podcast Server

A simple flask server for serving mp3 files as an RSS feed.

The idea was to create a simple HTTP service that would both dynamically create the RSS Feed and server the mp3 files  


Makes Use of https://podgen.readthedocs.io


# Create the environment
```shell script
pip install --user pipenv
git clone https://github.com/bgiaccio/podcasts.git
cd podcasts
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup.py sdist bdist_wheel
```
