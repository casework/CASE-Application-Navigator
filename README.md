## A stand alone application for humans to read JSON-LD files complied with the UCO/CASE  ontology. 

The JSON-LD files are almost complied with UCO version 0.6 and CASE 0.4, but the 
files are also based on the *not-in-ontology* space, conceived within 
the *INSPECTr project*. The application deals with the following Observables/Artifacts:

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
* SOCIAL MEDIA ACTIVITY (not in ontology yet)
* WEB HISTORY
* WIRELESS NETWORK 

The Artifacts are shown in a tree-view structure in a similar manner to reader tools provided by the most popular commercial forensic tools. The main aim of the viewer is to display the
JSON-LD content in a user-friendly manner and to carry out internal check on the expected data.

In the first part of the processing the tool carries out a formal check of the JSON file, relying on the load method of the module json.

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:


* codecs (UTF-8 and other codec management)
* json 
* PyQT5

## Usage

> *CASEviewer.py  JSON_INPUT*

where:

* JSON_INPUT is the file to be processed
