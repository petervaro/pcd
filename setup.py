from distutils.core import setup

with open('README.md') as readme:
    setup(name             = 'pcd',
          packages         = ['pcd'],
          version          = '0.1.1',
          description      = 'Python Contract Decorators',
          long_description = readme.read(),
          license          = 'LGPL-3.0',
          author           = 'Peter Varo',
          author_email     = 'hello@petervaro.com',
          url              = 'https://github.com/petervaro/pcd',
          download_url     = 'https://github.com/petervaro/pcd/archive/0.1.1.tar.gz',
          keywords         = ('contract', 'design', 'testing'))
