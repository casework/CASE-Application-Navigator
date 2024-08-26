## A GUI application based on QT5 to visualise JSON-LD files complied with the UCO/CASE ontology.

The JSON-LD files must be complied with the UCO/CASE version 1,3 but they are also based on the *drafting* namespace, aimed to represent artifact not included in the ontology yet. The application processes the following Artifacts:

* ACCOUNT
* CALL
* CELL SITE
* CHAT
* COOKIE
* EMAIL
* EVENT
* FILE (Image, Audio, Video, Text, Archive, Database, Application, Uncategorised)
* LOCATION DEVICE
* SEARCHED ITEM
* SOCIAL MEDIA ACTIVITY (in drafting namespace)
* WEB HISTORY
* WIRELESS NETWORK

The Artifacts are shown in a tree-view structure in a similar manner the forensic tools readers provided by the most popular commercial forensic tools do. The main aim of the viewer is to display the JSON-LD content in a user-friendly manner for checking the accuracy and the coverage of the conversion process, from XML (output of the commercial tool) to JSPN-LD.

In the first part of the processing the application carries out a formal check of the JSON-LD content, relying on the load method of the module json.

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:


* codecs (UTF-8 and other codec management)
* json
* PyQT5

## Usage

> *CASEviewer.py JSON_INPUT*

where:

* JSON_INPUT is the file to be processed.
