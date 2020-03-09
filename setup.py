#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

import shlex
import subprocess
import os.path
from setuptools import setup, find_packages

base_dir = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(base_dir, "src", "devsecops", "__about__.py"),
          encoding='utf-8') as f:
    exec(f.read(), about)

if os.path.isfile(os.path.join(base_dir, 'README.md')):
    with open(os.path.join(base_dir, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ''


def shell_run(command: str):
    return subprocess.check_output(shlex.split(command)).decode().strip()


def determine_version():
    os.chdir(base_dir)
    if os.path.isdir(os.path.join(base_dir, '.git')):
        try:
            pkg_ver = shell_run('git describe --tags --abbrev=0')
            latest_commit = shell_run(
                'git rev-list HEAD --no-walk --max-count=1'
            )
            latest_tag_commit = shell_run(
                'git rev-list --tags --no-walk --max-count=1'
            )
            if latest_commit != latest_tag_commit:
                pkg_ver += '.dev{}'.format(shell_run(
                    'git rev-list {}..HEAD --count'.format(latest_tag_commit)
                ))
            tree_dirty = shell_run('git diff HEAD')
            if tree_dirty != '':
                pkg_ver += '-DIRTY'
            return pkg_ver
        except subprocess.CalledProcessError:
            return about.get('__version__') + '-' + about.get('__release__')


setup(
    name=about['__name__'],
    version=determine_version(),
    description=about['__summary__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='devsecops redhat openshift',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6',
    install_requires=about['__requires__'],
    entry_points={
        'console_scripts': [
            'devsecops-api=devsecops.cli:main',
        ],
    },
)
