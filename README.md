# Soundcube
### A Raspberry Pi (or anything else, really)-hosted audio server
###### This is the backend repository, see [Soundcube-frontend](https://github.com/DefaultSimon/Soundcube-frontend) for the React frontend portion of this project.
![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)  

This is a work-in-progress project, no stability is guaranteed.

## Requirements
This project requires *Python 3.7+* as well *NodeJS* and *npm* (>= 10).

## Installation
*(This guide assumes you're using Linux)*

- clone this repository: `git clone https://github.com/DefaultSimon/Soundcube.git`  
- fetch the submodule(s): `git submodule init && git submodule update`
- install the required Python dependencies with [pipenv](https://github.com/pypa/pipenv): `pipenv install --python 3.7`
- make a production React build by running `cd frontend && ./build_production.sh`

After that, copy and modify the example configuration files in `data/` to proper extensions (from .ini.example to .ini), fill them out and you're done!  

Finally, run the Soundcube server using `run.sh`.
