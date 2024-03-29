import glob
import json
import logging
import os
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

import pytz
from dateutil.parser import isoparse
from podgen import Podcast, Person, Media, htmlencode


class PodcastService:
    def __init__(self, base_url:str, search_dir: str):
        self.base_url = base_url
        self.search_dir = search_dir
        self.logger = logging.getLogger(__name__)

    def generate_podcast(self, feed_name: str) -> str:
        """
        Create podcast XML based on the files found in podcastDir. Taken from
        https://podgen.readthedocs.io/en/latest/usage_guide/podcasts.html

        :param self: PodcastService class
        :param feed_name: name of the feed and the sub-directory for files
        :return:  string of the podcast
        """
        feed_dir = Path(self.search_dir).joinpath(feed_name)
        feed_metadata = feed_dir.joinpath("metadata.json")
        if feed_metadata.exists():
            with open(feed_metadata, encoding="utf-8") as feed_metadata_file:
                metadata = json.load(feed_metadata_file)
                if authors := metadata['authors']:
                    metadata['authors'] = []
                    for p in authors:
                        metadata['authors'].append(Person(p))
                p = Podcast(**metadata)
        else:
            # Initialize the feed
            p = Podcast()

            # Required fields
            p.name = f'{feed_name} Archive'
            p.description = 'Stuff to listen to later'
            p.website = self.base_url
            p.complete = False

            # Optional
            p.language = 'en-US'
            p.feed_url = f'{p.website}/feeds/{feed_name}/rss'
            p.explicit = False
            p.authors.append(Person("Anthology"))

            for ext in ['.jpg', '.png']:
                image_file_name = feed_dir.joinpath(f'{feed_name}.{ext}')
                if image_file_name.is_file():
                    p.image = f'{p.website}/{image_file_name.lstrip(self.search_dir)}'.replace(' ', '+')
                    break

            with open(feed_metadata, 'w', encoding='utf-8') as outFile:
                # Too many fields in Podcast so just write a subset
                data = dict(
                    name=p.name, description=p.description, website=p.website, complete=p.complete, language=p.language,
                    feed_url=p.feed_url, explicit=p.explicit, authors=p.authors, image=p.image
                )
                json.dump(data, outFile, indent=2, default=str)

        for path in feed_dir.glob('**/*.mp3'):
            filepath = str(path)
            episode = p.add_episode()

            # Attempt to load saved metadata
            metadata_file_name = filepath.replace('.mp3', '.json')
            try:
                with open(metadata_file_name) as metadata_file:
                    metadata = json.load(metadata_file)
            except FileNotFoundError:
                metadata = {}
            except JSONDecodeError:
                metadata = {}
                self.logger.error(f'Failed to read {metadata_file_name}')

            # Build the episode based on either the saved metadata or the file details
            episode.title = metadata.get('title', filepath.split('/')[-1].rstrip('.mp3'))
            episode.summary = metadata.get('summary', htmlencode('Some Summary'))
            if 'link' in metadata:
                episode.link = metadata.get('link')
            if 'authors' in metadata:
                episode.authors = [Person(author) for author in metadata.get('authors')]
            episode.publication_date = \
                isoparse(metadata.get('publication_date')) if 'publication_date' in metadata \
                else datetime.fromtimestamp(os.path.getmtime(filepath), tz=pytz.utc)
            episode.media = Media(f'{p.website}/{filepath.lstrip(self.search_dir)}'.replace(' ', '+'), os.path.getsize(filepath))
            episode.media.populate_duration_from(filepath)

            if "image" in metadata:
                episode.image = metadata.get('image')
            else:
                for ext in ['.jpg', '.png']:
                    image_file_name = filepath.replace('.mp3', ext)
                    if os.path.isfile(image_file_name):
                        episode.image = f'{p.website}/{image_file_name.lstrip(self.search_dir)}'.replace(' ', '+')
                        break

            # Save the metadata for future editing
            if not os.path.exists(metadata_file_name):
                metadata = {
                    'title': episode.title,
                    'summary': episode.summary,
                    'publication_date': episode.publication_date,
                    'authors': episode.authors,
                    'image': episode.image
                }
                with open(metadata_file_name, 'w', encoding='utf-8') as outFile:
                    json.dump(metadata, outFile, indent=2, default=str)

        return p.rss_str()


if __name__ == '__main__':
    podcast_service = PodcastService('http://localhost:9111', f'{os.environ["HOME"]}/Downloads')
    print(podcast_service.generate_podcast('podcasts'))
