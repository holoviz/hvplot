.. _devguide_release:

Releasing
=========

This chapter describes how to release a new package.

.. contents::
    :local:
    :depth: 2


For releasing new packages, we normally do an alpha release first. We check if 
there are any issues with the alpha release. If we don't see any issues, 
we then do an actual release. 

Alpha release
~~~~~~~~~~~~~

First, we create an annotated tag in Git by specifying `-a` when run the `git tag` command. 
We also specify `-m` for a tagging message. Please change the version 1.1.1a0 to the actual 
version number. 

.. code-block:: sh

    git tag -a -m “Version 1.1.1a0” v1.1.1a0

Then we push the tag to Github repo:

.. code-block:: sh

    git push origin v1.1.1a0



Actual release
~~~~~~~~~~~~~~~
If there are no issues with the alpha release, we can do an actual release with similiar steps. 

We create an annotated tag:

.. code-block:: sh

    git tag -a -m “Version 1.1.1” v1.1.1

To push the tag: 

.. code-block:: sh

    git push origin v1.1.1


To create a new release and add release notes:

* Go to the Github repository
* Click "Releases"
* Click "Tags"
* Click the most recent tag that you just added 
* Click "Create a new release"
* Add release notes and publish the release 



.. _contact the developers: https://gitter.im/pyviz/pyviz
.. _pytest: https://docs.pytest.org
.. _TravisCI: https://travis-ci.org/
