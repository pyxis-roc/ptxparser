# SPDX-FileCopyrightText: 2021 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-Contributor: Sreepathi Pai

from setuptools import setup, find_packages

setup(name='ptxparser',
      version='0.1',
      packages=find_packages(),
      scripts=['scripts/ptxfeatures.py']
)
