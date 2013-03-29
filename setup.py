# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(name='formskit',
          version='0.1',
          author=['Dominik "Socek" Długajczy'],
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          test_suite='formskit.tests.get_all_test_suite',
          )
