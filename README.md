# piper

`piper` is a manifest-based build system which is completely controlled from
configuration files local to a repository.

## Installation

As with any good Python project; `sudo pip install piper`.

## Rationale

*"Whatever you do, don't ever build a new build system. That would be the worst
possible thing to do."* - one of my managers, not realizing that telling
a hacker what they cannot do is the most inspiring thing that exists.

This is a project inspired by working with different build systems full-time
for a bit longer than a year. After trying to fit increasingly blob shaped pegs
into increasingly opinionated holes, a couple of thoughts started to form:

* Storing configuration anywhere but inside in the repository is a bad idea.
* Most modern build systems have too many concerns they probably should not
  have. The UNIX principle or anything like it was forgotten long ago. To this
  end, all build steps should be command lines and not builtin wrappers in
  whatever language the system is built in.
* The system needs to be runnable locally in the same manner as it would happen
  on any build agent, with actual execution if possible, or else in a dry-run
  mode.
* Inheritable templates are not the way to go, not at scale.
* Why did we leave the terminal? Wouldn't a curses interface be fantastic if
  done at least remotely right?
* [It can't be that hard][hard] to build a pipeline - the difficulty of
  the problem is overstated.

## Design

The meat of the application lies in the [YAML][yaml] configuration file
`piper.yml`, found in the root of the repository. Its contents dictate what
`piper` will do in its execution steps and in which order.

### Piper()

The main executor of the `piper` pipeline is the `Piper()` class. It's
a singleton (shut up) that reads the configuration and uses that configuration
to set and host a couple of other classes:

* `Env()`: Creates and tears the execution env. The env can be a temporary
  directory, an AWS machine, a schroot or something of the sort. Can optionally
  provide a wrapper method for `Step()` that all execution will run through,
  e.g. `schroot -c 'squeeze-amd64' -- {0}` to run something in a schroot.
* `Step()`: Executes a build step. `Piper()` has a list of these and will
  execute them in order. Each step can specify upstream and downstream steps
  that will deterministically build a graph of steps.
* `Notifier()`: Handles notifications and logging.

These classes are all written to be subclassed for more specific cases, such as
a `PythonStep()` class that builds Python projects, a `IRCNotifier()` class
that does just that, etc.


[hard]: https://github.com/thiderman/talk-hard
[yaml]: http://www.yaml.org/
