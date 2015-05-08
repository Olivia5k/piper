=====
Piper
=====

`piper` is a build agent that you can run locally!

Rationale
---------

*"Whatever you do, don't ever build a new build system. That would be the worst
possible thing to do."* - one of my managers, not realizing that telling
a hacker what they cannot do is the most inspiring thing that exists.

Build systems are a pervasive problem. Every single one of them has its pros
and cons and are both terrible and great in their own special way. Piper tries
to solve this problem in its own way, by focussing on providing a tool that
will allow you to easily reproduce builds locally and power a decentralised
build infrastructure.


How it works
------------

`piper` does two things:

* It's a build agent. It receives requests about things it should build and
  subsequently builds it. If you run `piperd start` it will start in daemon
  mode and start listening for requests.
* It's a build executor. It reads configuration files, figures out what to
  execute, and executes it. If you run `piper exec <pipeline>` it will build
  that pipeline for you locally.


Features
--------

This list of features is what we're working towards. A lot of them are already
in place.

* Configuration with code. The configuration to build your project is stored
  with the rest of the code. There is no difference between running it locally
  or on a build agent.
* Versioning: Since your configuration lives with your code, it has a version
  history just like the rest of your project.
* The project is the executor, the agent *and* the scheduler; you can run the
  exact same steps locally as a build agent would.
* Build pipelines are first-class citizens. Chaining builds together and
  triggering other builds upon success is the core of it all.
* Use your tools. A build just executes different commands for you. It doesn't
  hide what it does or impose a tool chain on you.
* API: everything is built on top of the same API, no exceptions.
* It has a CLI with completion support.
* Web UI to see build status, progress and retrigger builds.
* Lightweight: it starts in a couple of seconds.
* Distributed; all agents can receive requests to build anything, and they
  will sort out which agent should execute what builds. The only central point
  is a database.
* Logs are stored and can be viewed from a central location.

What it is built on
-------------------

Piper stands on the shoulders of other open source giants:

* Python_ 3.4+
* RethinkDB_
* Elasticsearch_

This whole project is written in Python 3.4, it is not compatible with older
versions of Python 3 or Python 2. We rely on new features in Python 3.4
including but not limited to asyncio_.

RethinkDB_ is the database of our choosing to store all kinds of information.
It scales well and has a very nice query language. Since we just end up
passing JSON_ around it fits our needs really well.

Elasticsearch_ is optional but can be used for build log storage. By default
logs are shipped off to RethinkDB instead but especially for bigger sites
storing and indexing that data into Elasticsearch can provide much more
insight into what's happening across your builds.


What piper does not do
----------------------

A lot of build systems end up becoming more and more complex because they want
to solve every single problem from build to deploy and everything in between
for you.

With Piper we chose to focus on being good at one thing, building your software,
and integrates with other tools to do the rest:

* Statistics and graphing
* Artifact storage
* Log storage and processing
* VCS tracking
* Issue tracking
* Code and test introspection

.. _Python: https://www.python.org
.. _RethinkDB: http://rethinkdb.com
.. _JSON: http://www.json.org
.. _Elasticsearch: https://www.elastic.co/products/elasticsearch
.. _asyncio: https://docs.python.org/3.4/library/asyncio.html
