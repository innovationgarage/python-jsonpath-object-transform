#!/usr/bin/env python

import setuptools

setuptools.setup(name='python-jsonpath-object-transform',
      version='0.1',
      description='JSON transformation using JSONPath',
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/python-jsonpath-object-transform',
      packages=setuptools.find_packages(),
      install_requires=[
          "jsonpath",
      ],
      include_package_data=True
  )
