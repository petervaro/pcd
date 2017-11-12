from distutils.core import setup

VERSION = '0.1.2'

with open('README.md') as readme:
    setup(name             = 'pcd',
          packages         = ['pcd'],
          version          = VERSION,
          description      = 'Python Contract Decorators',
          long_description = readme.read(),
          license          = 'LGPL-3.0',
          author           = 'Peter Varo',
          author_email     = 'hello@petervaro.com',
          url              = 'https://github.com/petervaro/pcd',
          keywords         = ('contract', 'design', 'testing'),
          download_url     = 'https://github.com/petervaro/pcd/'
                             'archive/{}.tar.gz'.format(VERSION))
