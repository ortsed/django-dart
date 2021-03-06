import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README.markdown'))
readme = f.read()
f.close()

setup(
    name='django-dart',
    version="1.0",
    description='django-dart is a reusable Django application for DoubleClick ad tags',
    long_description=readme,
    author='Llewellyn Hinkes-Jones',
    author_email='',
    url='https://github.com/ortsed/django-dart',
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
	include_package_data=True,
	zip_safe=False,
)

