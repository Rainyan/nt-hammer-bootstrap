# nt-hammer-bootstrap

An interactive GUI helper for setting up Source SDK and Hammer editor, for mapping for Neotokyo.

## Requirements

* Windows 10 or newer (older versions may work, but aren't officially supported)
* Steam has to be installed, and logged in

## Installation

* No installation required, just download the [latest release](https://github.com/Rainyan/nt-hammer-bootstrap/releases/latest) and run the executable file.

## Usage

* The entire process is automated, just read the instructions and click the buttons.

## For developers

### Licensing

Please see the LICENSE file for details. This project and its derivatives must use GPL, because our GUI library dependency is GPL.

### Setting up the environment

```bash
# Or use your fork, instead.
# Note that we have submodules that also need to be cloned here.
git clone --recurse-submodules https://github.com/Rainyan/nt-hammer-bootstrap
cd "./nt-hammer-bootstrap"
pip install --upgrade pipenv  # For virtualizing the dev environment
pipenv --three
pipenv run pip install --upgrade -r requirements.txt
pipenv run python nt_hammer_bootstrap.py  # Run app
```

### Building the executable

Please see the `.github/workflows` files for code on building the .exe binary.

