Beaglebone-Web-LED
==================

Beaglebone web server controlling LED.
For full tutorial see [http://aquaticus.info/beaglebone-web-led](http://aquaticus.info/beaglebone-web-led)

Installation
------------

These steps are valid for Ångström Linux.

	opkg update
	opkg install python-mmap
	opkg install python-distutils
	opkg install  python-compile
	wget http://download.cherrypy.org/cherrypy/3.2.2/CherryPy-3.2.2.tar.gz
	tar xzf CherryPy-3.2.2.tar.gz
	cd CherryPy-3.2.2
	python setup.py install
