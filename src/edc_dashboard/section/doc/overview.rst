Overview
========   

Module :mod:`bhp_section` add some default functionality to each section within the EDC.

The EDC usually has one or more sections that serve the study specific data collection such as "Subject" or "Maternal" and "Infant". 
These sections have a few things in common that are provided here. 
* need a link to add a consent or some registration document
* need to search on registration information to find subjects
* need to see a link to the subject's dashboard.

Also, there are common sections to the EDC. They are either registered here in this modules section.py or 
in the section.py of an INSTALLED_APP. Such sections include 'Statistics', 'Audit', 'Lab', and 'Administration'. 
