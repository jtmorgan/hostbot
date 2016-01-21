try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'MatchBot',
    'author': 'Frances Hocutt',
    'url': 'https://github.com/fhocutt/matchbot',
    'download_url': '',
    'author_email': 'frances.hocutt+matchbot@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['matchbot'],
    'scripts': [],
    'name': 'MatchBot'
}

setup(**config)
