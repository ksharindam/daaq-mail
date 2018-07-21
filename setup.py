
from setuptools import setup
from daaq import __version__


setup(
      name='daaq',
      version=__version__,
      description='A lightweight Mail Client',
      long_description='A lightweight Mail Client',
      keywords='email pyqt pyqt4 qt4',
      url='http://github.com/ksharindam/daaq-mail',
      author='Arindam Chaudhuri',
      author_email='ksharindam@gmail.com',
      license='GNU GPLv3',
      packages=['daaq'],
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications :: Qt',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['daaq=daaq.main:main'],
      },
      data_files=[
                 ('share/applications', ['files/daaq-mail.desktop']),
                 ('share/icons', ['files/daaq-mail.png'])
      ],
      include_package_data=True,
      zip_safe=False)
