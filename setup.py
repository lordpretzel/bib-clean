from setuptools import setup

package = 'bibclean'
version = '1.0'
requirements = [
          'bibtexparser',
      ]
setup(name=package,
      version=version,
      description="Tool for cleaning up bibfiles",
      install_requires=requirements,
      packages = [ 'bibclean' ],
      entry_points={
          'console_scripts': [
              'cleanbib = bibclean.bibclean:main',
          ],
      },
      url='url')
