from setuptools import setup, find_packages

def readme():
  with open('README.md') as f:
    return f.read()

import sys
if not sys.version_info[0] == 3:
  sys.exit("Sorry, only Python 3 is supported")

setup(name='prenacs',
      version='1.0.2',
      description='PRovenance-tracking ENtity "+\
                  "Attribute batch Computation and database Storage system',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/ggonnella/prenacs',
      keywords="batch computing, database, data provenance",
      author='Giorgio Gonnella',
      author_email='gonnella@zbh.uni-hamburg.de',
      license='ISC',
      # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
      ],
      packages=find_packages(),
      scripts=['bin/prenacs-load-results',
               'bin/prenacs-batch-compute',
               'bin/prenacs-check-plugin',
               'bin/prenacs-drop-attribute',
               'bin/prenacs-create-attribute',
               'bin/prenacs-setup-database',
               'bin/prenacs-manage-attributes'],
      zip_safe=False,
      test_suite="pytest",
      include_package_data=True,
      tests_require=['pytest', 'pytest-console-scripts'],
    )
