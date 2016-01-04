=============================
yowlayer-django-store
=============================

.. image:: https://badge.fury.io/py/yowlayer-django-store.png
    :target: https://badge.fury.io/py/yowlayer-django-store

.. image:: https://travis-ci.org/jlmadurga/yowlayer-django-store.png?branch=master
    :target: https://travis-ci.org/jlmadurga/yowlayer-django-store
    
.. image:: https://codecov.io/github/jlmadurga/yowlayer-django-store/coverage.svg?branch=master
	:alt: Coverage
    :target: https://codecov.io/github/jlmadurga/yowlayer-django-store?branch=master
    
.. image:: https://requires.io/github/jlmadurga/yowlayer-django-store/requirements.svg?branch=master
     :target: https://requires.io/github/jlmadurga/yowlayer-django-store/requirements/?branch=master
     :alt: Requirements Status

Storage layer for yowsup in django. Based on https://github.com/tgalal/yowlayer-store.

Documentation
-------------

.. image:: https://readthedocs.org/projects/yowlayer-django-store/badge/?version=latest
        :target: https://readthedocs.org/projects/yowlayer-django-store/?badge=latest
        :alt: Documentation Status

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
* Media messages added

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

