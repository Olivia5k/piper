=====================
Contributing to piper
=====================

Development environment
-----------------------

`piper` uses a straight-forward Python setup. pyenv_ and virtualenv_ are
recommended.

Once in a virtualenv, the tests can be run by `python setup.py test`, which
will download all dependencies.

Code and code guidelines
------------------------

`piper` tests itself, of course! If `piper` can build itself with `piper exec`,
your code is welcome in a Pull Request!

Things to generally think about:

* Code is always welcome, and discussing in an issue before implementing is
  encouraged.
* Commit messages should follow the convention_.
* Unit tests are required, integration tests are encouraged.
* If unsure, strive to emulate the look and feel of the rest of the code.
  Consitency is king!

Test naming
^^^^^^^^^^^

All functions have a corresponding test class in the corresponding test file:

.. code-block:: python

   # in piper/lazer.py
   class Lazergun():
       def pewpew(self):
           # <code>

maps to

.. code-block:: python

   # in test/test_lazer.py
   class TestLazergunPewpew():
       def test_pewpew_case(self):
           # <test>
       def test_pewpew_another_case(self):
           # <test>

The mapping is basically making a test class called
`Test` + `<class name` + `<method name in CamelCase>`
and adding one test case for all of the cases in that method.
Using this mapping makes it possible to use tooling to navigate
between tests and code, making developers happy!

Issue management
----------------

Creating issues is welcome. Don't worry about accidentally adding a duplicate -
the collaborators will sort that out without a hitch! It's better to ask
than not to ask! You also don't need to add labels - the contributors will help
out with that as well.

The discussions_ label means that something requires input, and that input
can come from you even though you have not contributed to the project in any
other sense before!

If you start working on something, add yourself as the assignee so that it's
visible what is being worked on or not.

Collaborators
-------------

If you are a collaborator, there are some extra guidelines:

* React on issues. Reply to them if possible and add labels accordingly. Assign
  users if they are working on something but did not add themselves.
* Avoid pushing to master without a Pull Request. Use branches on the repo
  freely.


.. _pyenv: https://github.com/yyuu/pyenv
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _convention: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _discussions: https://github.com/thiderman/piper/labels/discussion
