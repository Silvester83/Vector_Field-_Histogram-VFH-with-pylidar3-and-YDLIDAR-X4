# TUGAS-AKHIR
this code is an implementation of Vector Field Histogram algorithm in Python programming language
the sensor used in this implementation is YDLIDAR X4 sensor from EAI
PyLidar3 library needs to be installed to use this algorithm
the plot used in this program is using PyQtgraph from PyQt4

there's an issue in this program which comes from the library used, 
the PyLidar3 library used in this implementation averages all the reading in 1 degree angle range
and it causes missreadings at some object boundary
