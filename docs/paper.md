Prenacs: a Python package for provenance-tracking computation and
storage of attributes of entities

# Statement of need

Reproducibility is a key request for scientific research. This is particularly
challenging in fields of research where a large number of computations are
performed producing heuristic results, such as in Applied Bioinformatics.

Several solutions are routinely used for documenting the production of results.
E.g. interactive computations can be documented and often reproduced by storing
the computation history in Jupyter notebooks (CIT). This solution is ideal,
when a fixed set of computations is run, e.g. for analysing a given dataset. In
contrast, it is not well suited for a dynamic input, such as entries in a
biological sequence database, for which new computations are incrementally run
from time to time.

Alternatively, pipeline management systems, such as Snakemake (CIT) can be used
to define workflows for the analysis, which can be re-applied easily to new
data. However, such systems do not define a system for storing the results,
alongside with the code which computed them.

Prenacs was developed to solve these problems by providing a flexible and
extensible system for batch computations, allowing for incremental computations
and changes in the computation code, combined with a database storage solution
which records the provenance of each result.

# Main features

Prenacs allows to compute and store computation results (called _attributes_)
for each of a set of objects, called _entities_. Each entity must be
characterized by an identifier, which must be unique in the context.

The input of the computation can be provided in different ways, e.g. as a list
of entity identifiers, which could e.g. be used for interacting with an
external database REST API, or as a set of files, with filenames which can be
assigned to the entities by their identifiers.

The code necessary for the computations is provided to Prenacs by the user
as a _plugin_: the documentation defines the interface of a plugin and provides
scripts to check that a plugin is correctly implemented. Plugins can be
written in multiple languages (Python, Bash, Rust, Nim) and can be both
thin wrappers calling external programs or directly compute the values.
Using a versioning system, the plugin code can be updated, without loosing
the provenance information for existing data computed using the older
versions of the plugin.

The results of the computation are stored in a database, alongside all
provenance tracking information. For each batch computation, an UUID is
generated, which is stored alongside each data point of the results, or group
of results. A table stores the metadata of the batch computations, including
input size, running time measurements, system name, user name, and references
to the plugin used for the computation (name and version). The plugin table
stores the metadata and code of each plugin in a given version.

The results of each computation must be single or multiple values. Each value
or group of related values is an _attribute_ of the input entity. Attribute
values can have multiple data types: they can be scalars, e.g. integers,
floats, boolean, strings, or compound values, such as homogeneous arrays of
values of the same type or heterogeneous sets of values. The attribute
definition, including their description, datatype and optional links to
ontologies are managed by Prenacs and stored in the database.

Due to the extensibility using a plugin system, the list of attributes and their
datatypes are not known in advance. One solution for storing such data in a
database is the entity-value model. However, this also has a number of
disadvantages, such as the inability to index the data - thus this model was
not used. Instead, to ensure a good performance, a storage system was
developed, with attributes stored in columns of a set of tables. New columns
are added automatically when new attributes are defined. To avoid an excessive
number of columns, the attributes are automatically spread across multiple
tables, which are automatically managed.

## Code organization

Prenacs was developed as a collection of Python packages. The main functionality
is provided by the ``prenacs`` package. All functionality upon which ``prenacs``
is based, which could be useful in different contexts, was developed as separate
packages.

The code for performing batch computations is provided to Prenacs in form of
plugins. The plugin system was developed as a separate package, named
``multiplug``, allowing to develop plugins for Python programs in multiple
programming languages (Python, Bash, Rust and Nim).

The results of batch computations are stored in a database in a set of tables,
automatically managed, to which columns can be added dynamically, and which
allows storing a provenance identifiers for single data points or group of data
computed together. This storage system was developed as a separated package,
named ``attrtables``.

## Misc / Notes (this must be cleaned up)

An user manual is provided for Prenacs, as well as for the undelying packages
multiplug and attrtables.

A test suite is provided for each of the packages.

Requirements: Prenacs was developed using MariaDB. Although it is in principle
possible to use another RDBMS - since it was implemented using SQLAlchemy - it
was not tested using that.

For performance reasons, the computation results are not stored immediately in the
database. They are instead batch loaded into the database after the computation.

Parallel computation is supported.

It can be used from the command line or using an API from inside a Python program.

Provided functionality:
- check plugin
- batch compute
- load results
- setup database, destroy database
- create attribute, drop attribute, manage attributes

Main ideas of Prenacs
- a set of entities, for which attributes are computed
- attributes can be recomputed, but only the newest value is relevant
- attribute definitions are dynamic
- the computation can be done in different programming languages

Current systems include:
- flexible workflow management systems, GUI-based (eg. Galaxy, Taverna, Knime)
or programming-based (e.g. Nextflow, Snakemake).

The functionality provided by Prenacs can be implemented in those systems.
However, Prenacs does not aim to be a general-purpose workflow management system.
Instead, it aims at doing a single thing (storing information about
a set of entities) and doing it in a simple and reproducible way.
