from setuptools import setup, find_packages

def readme():
  with open('README.md') as f:
    return f.read()

import sys
if not sys.version_info[0] == 3:
  sys.exit("Sorry, only Python 3 is supported")

setup(name='provbatch',
      version='1.0',
      description='Batch computing and results storage system with provenance-tracking',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/ggonnella/provbatch',
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
      scripts=['bin/pvb-load-results',
               'bin/pvb-batch-compute',
               'bin/pvb-check-plugin',
               'bin/pvb-drop-attribute',
               'bin/pvb-create-attribute',
               'bin/pvb-manage-attributes'],
      zip_safe=False,
      test_suite="pytest",
      include_package_data=True,
      tests_require=['pytest', 'pytest-console-scripts'],
    )
