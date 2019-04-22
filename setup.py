from distutils.core import setup
setup(
  name = 'dl_jobs',
  packages = ['dl_jobs'],
  version = '0.0.0.1',
  description = 'DescartesLabs: Task Manager',
  author = 'Brookie Guzder-Williams',
  author_email = 'bguzder-williams@wri.org',
  url = 'https://github.com/brookisme/dl_jobs',
  download_url = 'https://github.com/brookisme/dl_jobs/tarball/0.1',
  keywords = ['DescartesLabs'],
  include_package_data=True,
  data_files=[
    (
      'config',[]
    )
  ],
  classifiers = [],
  entry_points={
      'console_scripts': [
          'dl_jobs=dl_jobs.cli:cli'
      ]
  }
)