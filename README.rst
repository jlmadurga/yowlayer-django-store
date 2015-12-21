=============================
yowlayer-django-store
=============================

.. image:: https://badge.fury.io/py/yowlayer-django-store.png
    :target: https://badge.fury.io/py/yowlayer-django-store

.. image:: https://travis-ci.org/jlmadurga/yowlayer-django-store.png?branch=master
    :target: https://travis-ci.org/jlmadurga/yowlayer-django-store

Storage layer for yowsup in django. Based on https://github.com/tgalal/yowlayer-store.

Documentation
-------------

The full documentation is at https://yowlayer-django-store.readthedocs.org.

Quickstart
----------

Install yowlayer-django-store::

    pip install yowlayer-django-store
    
Include in your django apps::
	
	INSTALLED_APPS = ( 
		...
		'yowlayer_store',
		...
		)

		
To use it in a project::

    import yowlayer_store


Features
--------

* Models for Text messages, convsersations and contact.

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

