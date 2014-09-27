# piper

`piper` is a build agent that you can run locally!

## Huh?
`piper` does two things:
* It's a build agent. It recieves requests about things it should build and
  subsequently builds it. If you run `piperd start` it will start in daemon
  mode and start listnening for requests.
* It's a build executor. It reads configuration files, figures out what to
  execute, and executes it. If you run `piper exec <pipeline>` it will build
  that pipeline for you locally.


### Selling points
* Build configuration is in the repository. This gives it versioning and anyone
  with the repository has access to the steps required to build it.
* The project is the executor, the agent *and* the scheduler; you can run the
  exact same steps locally as a build agent would.
* Build pipelines are first-class citizens. Chaining builds together and
  triggering other builds upon success is one of the main features.
* The configuration is completely centered on running other command lines as
  subprocesses. Whatever step is having troubles, you should be able to run the
  same command yourself.
* The main interface is the command line, and there is completion!
* It's lightweight and starts in less than a second.
* It's distributed; all agents can recieve requests to build anything, and they
  will sort out which agent should execute what builds. The only central point
  is a database.

### Things piper lets other systems do better
* Statistics and graphing
* Artifact storage
* Log storage and processing
* VCS tracking
* Issue tracking
* Code and test introspection

That said, `piper` has lots of helpful facilities to send data to the systems
that do these things better.


## Installation

`pip install piper`


## Rationale

*"Whatever you do, don't ever build a new build system. That would be the worst
possible thing to do."* - one of my managers, not realizing that telling
a hacker what they cannot do is the most inspiring thing that exists.

## Design

The meat of the application lies in the [YAML][yaml] configuration file
`piper.yml`, found in the root of the repository. Its contents dictate what
`piper` will do in its execution steps and in which order.

### Build()

The main executor of the `piper` pipeline is the `Build()` class. It reads the
configuration and uses that configuration to configure some runner classes:

* `Env()`: Creates and tears the execution environemnt. The environment can be
  a temporary directory, an AWS machine, a schroot or something of the sort.
  Can optionally provide a wrapper method for `Step()` that all execution will
  run through, e.g. `schroot -c 'squeeze-amd64' -- {0}` to run something in
  a schroot.
* `Step()`: A build step. `Build()` has a list of these and will
  execute them in order.

[yaml]: http://www.yaml.org/
