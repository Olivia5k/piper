# piper

`piper` is a manifest-based build system which is completely controlled from
configuration files local to a repository.

## Rationale

*"Whatever you do, don't ever build a new build system. That would be the worst
possible thing to do."* - one of my managers, not realizing that telling
a hacker what they cannot do is the most inspiring thing that exists.

This is a project inspired by working with different build systems full-time
for a bit longer than a year. After trying to fit increasingly blob shaped pegs
into increasingly opinionated holes, a couple of thoughts started to form:

* Storing configuration outside of the repository is ridiculous.
* The system needs to be runnable locally in the same manner as it would happen
  on any build agent, at least in a dry-run mode.
* Inheritable templates are not the way to go, not at scale.
* [It can't be that hard][naivete] to build a pipeline - the difficulty of
  the problem is overstated.

[naivete]: http://thiderman.org/posts/naivete/
