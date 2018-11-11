# Birst Upload and Processing
project, define its purpose, and outline the basic functionality.

This project consists of a set of re-usable Python scripts which achieve the following functionality:
1. Upload data to Birst
2. Process data in Birst
3. Provision Users via Birst Web Services


### Versioning Scheme

Scheme: Major.Minor.Patch version

|Version Number Category|Description|
|:---                   |:---       |
|Major| Major change involves full release cycle|
|Minor|Minor change involves addition of new feature or major behavior change|
|Patch Version|Patch Version number increases when bug fixes are incorporated|

### Contributors

+ Archana Balachandran (abalachandran@mycervello.com)
For any questions or enhancement requests, contact abalachandran@mycervello.com.

### Enhancement Requests : DJO

Usecase: At DJO, there's a script for multiple spaces - therefore, need to maintain multiple .py and .ini files per space
+ Pass spacename as parameter to the pipeline. Use that for creating Birst log and for dynamically assigning config file name. 
+ Or pass config file as a parameter to the script. 

