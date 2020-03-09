#!/bin/bash
quiet_run=''
update_only=''
get_pip=''
python=''
msg=''

function print_usage() {
    echo "usage: $0 [-h] | [-q] [-u] [-d] [-p PYTHON]"
}
function print_help() {
    print_usage
    cat << ENDOFHELP
$(basename $0) - a Virtualenv Bootstrapper

DESCRIPTION:
Makes a virtualenv wherever you've got a python setuptools/distutils package
  and installs that package, using the adjacent setup.py, into the virtualenv.

OPTIONS:
    -h          Print this help page and exit
    -q          Suppress the banner and extra spacing/help (quiet)
    -u          Update the package only - otherwise rebuild the venv
    -d          Install the package in debug mode for easy updates
    -p PYTHON   Specify the python interpreter to build the venv with
ENDOFHELP
}

while getopts "hqudp:" opt; do
    case "$opt" in
        h)
            print_help
            exit 0
            ;;
        q)
            quiet_run=true
            ;;
        u)
            update_only='true'
            ;;
        d)
            develop_mode='true'
            ;;
        p)
            python="${OPTARG[@]}"
            $python -m pip --help &>/dev/null || get_pip=true
            ;;
        *)
            print_usage >&2
            exit 1
            ;;
    esac
done

# Always start with a sane place
cd $(dirname $(realpath $0))
# Some tooling
. formatter

# We really want setup.py.
if [ ! -e setup.py ]; then
    wrap "No setup.py detected adacent to the script in $(pwd), check " \
         "\`$0 -h\` for more information." >&2
    exit 1
fi

# Shorted than writing the fmt every time
function now() {
    date '+%Y%m%dT%H%M%S'
}

# ERR cleanup helper
function on_error() {
    [ -n "$msg" ] && wrap "$msg" ||:
    echo
    now=$(now)
    mv $log mkvenv_error_$now.log
    sync
    wrap "Error on mkvenv.sh line $1, logs available at" \
         "$(pwd)/mkvenv_error_$now.log" >&2
    wrap 'Press Enter or Space to view the logs now,' \
         'or any other key to quit.' >&2
    read -sn1 quit_var
    [ -z "$quit_var" ] && less "$(pwd)/mkvenv_error_$now.log" ||:
    echo
    exit $2
}

# Look for things
function in_path() {
    which "${@}" &>/dev/null
    return $?
}

# Try to find the right python if it's not specified, but always accept any
# cli-passed value first as "probably right" and let the user deal with the
# consequences of their actions.
function check_python() {
    if [ -z "$python" ]; then
        if grep -qF 'Python :: 3' setup.py; then # assume we need python3
            if in_path python3; then
                python=python3
            elif ! in_path python; then
                echo 'No python detected, unable to continue'
                exit 1
            elif python --version | grep -qF '^Python 3'; then
                python=python
            elif grep -qF 'Python :: 2' setup.py; then # python2 acceptable
                python=python
            else
                echo "No suitable version of python found for setup.py, " \
                     "consider specifying path manually (check \`$0 -h\` " \
                     "for more information)"
                exit 1
            fi
        else # Just find python of some sort
            if in_path python; then # Just trust whatever the system/user has
                python=python
            elif in_path python3; then # We should prefer 3 tbh
                python=python3
            elif in_path python2; then # Last resort
                python=python2
            else
                echo "No suitable version of python found for setup.py, " \
                     "consider specifying path manually (check \`$0 -h\` " \
                     "for more information)"
                exit 1
            fi
        fi
    fi
    echo "Identified python: $python"
    # As an aside - do you guys have pip?
    $python -m pip --help &>/dev/null || get_pip=true
    $python -m virtualenv --help &>/dev/null || get_pip=true
    $python -c 'import setuptools' --help &>/dev/null || get_pip=true
    [ -n "$get_pip" ] && echo "pip needs installed" || echo "pip is installed"
}

# Some people don't have pip installed and virtualenv/setuptools configured?
# What is this, 1910? Whatever, we'll fix it.
function install_pip() {
    if ! curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py ; then
        msg=$(echo "Unable to download the pip installation bootstrapper, " \
              "ensure curl is installed and in the path and that you have " \
              "internet access.")
        return 1
    elif ! $python get-pip.py --user ; then
        msg=$(echo "Unable to install pip in user mode, ensure that you " \
              "have at least $python-distutils installed through your " \
              "operating system package manager (yum, apt, etc.)")
        return 2
    fi
    $python -m pip install --user --upgrade pip virtualenv setuptools \
        || return 3
}

# Stage some logging
log=$(mktemp)
exec 7>$log
echo "Logging initialized $(now)" >&7

# Set some traps
trap 'on_error $LINENO $?' ERR
trap 'rm -f $log' EXIT


# Showtime
if [ -z "$quiet_run" ]; then
    center_border_text 'Virtual Environment Creator'
    echo
fi

# Try to clean up environment variables and whatnot
if [ -z "$update_only" ]; then # Burn it to the ground
    warn_run 'Checking for (and unsetting) existing virtualenv' \
        '[ -n "$VIRTUAL_ENV" ] && { deactivate ; false ; } ||:'
    error_run 'Removing old virtual environment (if it exists)' rm -rf venv
fi

# Smart python detection
error_run 'Identifying python interpreter to use' check_python
if [ -n "$get_pip" ]; then # you should feel ashamed
    error_run 'Installing pip, virtualenv, and setuptools in pip user mode' \
        install_pip
fi

# Try to read setup.py, see what we can find
error_run 'Checking for valid setup.py' 'pkg_name=$($python ./setup.py --name)'
if [ -z "$update_only" ]; then # let's make it
    error_run "Making $python virtual environment" \
        "$python -m virtualenv -p $python venv"
else # Make sure it's set up
    error_run "Checking for existing $python virtual environment" \
        [ -x venv/bin/python ]
    # and clean
    error_run "Removing old site-package for $pkg_name" \
        "rm -rf venv/lib/python*/site-packages/$pkg_name{.egg,.egg-link}"
fi
# Ensure everything's up to date, infrastructure-wise
error_run 'Updating base venv packages' \
    venv/bin/python -m pip install --upgrade pip virtualenv setuptools

# Hard requirements definitions handled
if [ -f requirements.txt ]; then
    error_run "Installing requirements" \
        venv/bin/python -m pip install -r requirements.txt
fi

# Actual installation
if [ -n "$develop_mode" ]; then # egg-link mode
    error_run "Linking $pkg_name to venv in develop mode" \
        venv/bin/python ./setup.py develop
else # Normal distutils sdist/setuptools egg installation mode
    error_run "Installing $pkg_name to venv" \
        venv/bin/python ./setup.py install
fi

if [ -z "$quiet_run" ]; then
    echo
    wrap "Your virtualenv should be ready to go. To use $pkg_name, ensure you" \
        "activate the virtualenv, for example with:"
    echo '. '$(dirname $(realpath "$0"))'/venv/bin/activate'
fi
