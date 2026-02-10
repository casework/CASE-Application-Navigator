## A stand alone application for humans to read JSON-LD files complied with UCO/CASE ontology.

The JSON-LD files are almost complied with UCO and CASE version 1.4, but the
files are also based on the *drafting* space (http://example.org/ontology/drafting/), conceived by the community. The application deals with the following Observables/Artifacts:

* ACCOUNT
* APPLICATION
* BLUETOOTH CONNECTION
* BROWSER BOOKMARK
* CALENDAR
* CALL
* CELL SITE
* CHAT
* COOKIE
* DEVICE
* EMAIL
* EVENT
* FILE (Image, Audio, Video, Text, Archive, Database, Application, Uncategorised)
* LOCATION DEVICE
* SEARCHED ITEM
* SOCIAL MEDIA ACTIVITY
* WEB HISTORY
* WIRELESS NETWORK

The Artifacts are shown in a tree-view structure in a similar manner to reader tools provided by the most popular commercial forensic tools. The main aim of the viewer is to display the JSON-LD content in a user-friendly manner and to verify the accuracy and completeness of the XML report exported by the forensic tool.

In the first part of the processing the tool carries out a formal check of the JSON file, relying on the load method of the module json.

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:

* codecs (UTF-8 and other codec management)
* json
* PyQT6

The package dependencies is controlled by using *Poetry*. Poetry helps you create new projects or maintain existing projects while taking care of dependency management for you. It uses the *pyproject.toml* file, which has become the standard for defining build requirements in modern Python projects.


## Usage

> *CASEviewer.py <JSON-LD-FILE>*

where:

* JSON-LD-FILE is the JSON-LD file to be processed.
