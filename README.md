# devsecops-api-script
---
This script is designed to manipulate the APIs for the services stood up for the DevSecOps on OpenShift Container Platform 4 workshop.

It exposes several classes to manipulate those APIs with functions to manipulate the APIs using a context manager.

Additionally, there is a CLI based on `click` that helps to manipulate these APIs from the command line.

You can clone this repository and run `./mkvenv.sh -d` to install it into a Python 3 virtual environment. Once you source the venv, as the script prompts you to, you can run the CLI. Documentation is currently only included in the help pages. Sphinx docs may end up generated.
