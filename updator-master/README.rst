Updator
-------

Always be up-to-date!

Updator is a tool for automatically upgrade python libraries. It defines API changes rules which are actually python patterns (with some extras) that will transform into an ast. The rules were designed to be written by the libraries’ authors, but that will happen later on. What it does is basically just transforming the python code, that should be upgraded into an AST, and search the rules ast within the source code ast. If a rule ast is found - it’s transforming the pattern into a new pattern.

**Install the package:**


``pip install updator``

**To Use Updator:**


``updator run [lib] [path]``

where:
  - lib is the library you want to upgrade
  - path is the path for your code file you want to upgrade 
