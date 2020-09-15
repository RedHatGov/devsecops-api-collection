# devsecops-api-collection

This collection is designed to manipulate the APIs for the services stood up for the DevSecOps on OpenShift Container Platform 4 workshop.

It exposes several classes to manipulate those APIs with functions to manipulate the APIs using a context manager. These classes are the basis of Ansible modules in this collection.

Additionally, there is a CLI based on `click` that helps to manipulate these APIs from the command line. This CLI uses the same backend but is distributed as PyPi package and can be run from the shell.

## NOTE

The Ansible Collection is... not actually done. This is a work in progress. The script works. 🙂
