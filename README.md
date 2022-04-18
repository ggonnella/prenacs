# Prenacs

Prenacs is a system, which allows to run batch computations of attribute
values for sets of entities, and to store the computation results in a
database, alongside metadata which allows to track the data provenance.

The name is an acronym for
"PRovenance-tracking ENtity Attrtibute Computation and Storage system".

## Key concepts

_Entities_ are thereby object of any kind, characterized by an identifier,
which allows distinguishing the object from other objects of the same kind.
For each entity, ProBatch allows to compute the values of attributes.

_Attribute_ are properties of the entity. Anything whose value can be
determined using a computation (in a general sense, thus e.g. also obtaining
the value from an external data source) is an attribute. Each attribute may
consist of a single value (_scalar attribute_) or or multiple values
(_composite attribute_). The attribute system is open and flexible, i.e. new
attributes can be added at any moment.

ProvBatch allows to store a _single instance_ of each attribute for an entity:
that is, it is not meant to store multiple measurements of a value or
to store a journal of previous attribute computation results.

Alongside the computation results, ProBatch allows to track the _provenance_ of
attribute values. For achieving this, the code for attribute value computation
must be implemented in form of a _computation plugin_. Multiple plugins
may be available for computing the same attribute. A plugin may compute one
or multiple attributes. Plugins contain the code for the attribute computation,
as well as metadata, describing the input, output, supported paramaters and
methods and implementation notes. Whenever a plugin code changes, a
new _plugin version number_ is assigned.

Batch computation metadata instances are identified by an unique identifier
(UUID) and include a reference to a given plugin (plugin identifier and version
number), alongside information such as the computation parameters, timestamps,
identifier of the user starting the computation, and key system data.
Thus, storing the batch computation UUIDs alongside with computation results,
ProvBatch allows to keep track of the data provenance.

## Related libraries

Prenacs has been developed as part of an ecosystem of Python libraries,
including:
- _multiplug_, which implements the infrastructure for the plugin system
- _attrtables_, which implements the infrastructure for the storage of
  attribute values and metadata
- _snacli_, which is used for implementing double-purpose scripts, callable
  interactively from the command line, as well as inside a Snakemake pipeline

## Usage

The usage of the library is explained in the
 [user manual](https://github.com/ggonnella/prenacs/blob/main/docs/usage.md).
