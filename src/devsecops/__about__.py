# SPDX-License-Identifier: BSD-2-Clause

__all__ = [
    '__title__',
    '__name__',
    '__summary__',
    '__uri__',
    '__version__',
    '__status__',
    '__author__',
    '__email__',
    '__license__',
    '__copyright__',
]


__title__       = "devsecops-api"  # noqa: E221
__name__        = __title__  # noqa: E221
__summary__     = "DevSecOps Workshop API Collection"  # noqa: E221
__uri__         = "https://github.com/RedHatGov/devsecops-api-collection"  # noqa: E221,E501
__version__     = "0.2.0"  # noqa: E221
__release__     = "alpha"  # noqa: E221
__status__      = "Development"  # noqa: E221
__author__      = "James Harmison"  # noqa: E221
__email__       = "jharmison@redhat.com"  # noqa: E221
__license__     = "BSD-2-Clause"  # noqa: E221
__copyright__   = "2020 %s" % __author__  # noqa: E221

__requires__ = [
    'click',
    'requests'
]
