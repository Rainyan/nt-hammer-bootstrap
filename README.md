# nt-hammer-bootstrap

An interactive GUI helper for setting up Source SDK and Hammer editor, for mapping for Neotokyo.

This tool automates the entire mapping tools setup described in [this Steam guide](https://steamcommunity.com/sharedfiles/filedetails/?id=282059949).

![Example of the app GUI window](https://user-images.githubusercontent.com/6595066/203887912-53c742fa-2fa0-4e78-b34c-e035bb8d95dd.png)

## Requirements

* Windows 10 or newer
  * Older Windows versions may work, but aren't officially supported
  * For Linux, you may be able to run this in the same Wine prefix as your Windows tooling, but this remains untested as of now
* Steam has to be installed, and logged in

## Installation

* No installation required, just download the [latest release](https://github.com/Rainyan/nt-hammer-bootstrap/releases/latest) and run the executable file.

## Usage

* The entire process is automated, just read the instructions and click the buttons.

## Contributing

### Bug reports
If you have questions/feature requests, or run into problems, [bug reports](https://github.com/Rainyan/nt-hammer-bootstrap/issues) are welcome!

### For developers

#### Project licensing

Please see the [LICENSE](LICENSE) file for details. This project and its derivatives must use GPL, because our GUI library dependency is GPL.

#### Setting up the environment

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

#### Building the executable

Please see the [.github/workflows](.github/workflows) files for code on building the .exe binary.

### Acknowledgements

This project uses the following open-source software:
* [valve-keyvalues-python](https://github.com/gorgitko/valve-keyvalues-python)
* [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
