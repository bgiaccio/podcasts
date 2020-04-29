import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="podcast_server-bgiaccio",
    version="0.0.1",
    install_requires = ['Flask', 'podgen'],
    author="Brad Giaccio",
    author_email="brad.giaccio+podcast_server@gmail.com.com",
    description="Flask Podcast Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bgiaccio/podcasts",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)