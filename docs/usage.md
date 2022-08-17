# Prenacs User manual

## Implementing a plugin

In order to perform a computation, a _plugin_ must be implemented. A plugin
determines how one or multiple attributes of entities are computed.
Furthermore, it contains metadata, which is stored alongside the computation
results, in order to document the data provenance.

The plugin system is generic and implemented as a separate package,
named ``MultiPlug``. Plugins for Prenacs must implement a specific interface,
which is described in the
[plugin implementation guide](https://github.com/ggonnella/prenacs/blob/main/docs/plugin.md).

If a plugin which had been already used for computations changes,
its version number must be incremented, so that a new plugin metadata
record is created, when the new computation results are loaded into the
database.

### Checking the plugin implementation

In order to check if a plugin has been implemented correctly, it is possible
to use the ``prenacs-check-plugin`` script. This loads the plugin module and
analyses the exposed programming interface of the plugin, reporting
any error to the user.

## Database setup

The library was designed and tested using MariaDB. Other database
management systems can be used, in which case some adjustments may be needed.
The database must be already setup before the library can be used.
The database server must be started.

The following parameters are passed
to the scripts, which connect to the database:
- ``--dbuser``: database user to use
- ``--dbpass``: password of the database user
- ``--dbname``: database name
- ``--dbsocket``: connection socket file
- ``--dbpfx``: database tables prefix

Before the first use, the script ``prenacs-setup-database`` must be run,
which creates the necessary metadata tables.

## Managing the attributes

Before running a computation, the attributes which are computed by the
computation plugin must be added to the database.

For this a ``prenacs-manage-attributes`` script is provided.
The attributes metadata must be described in a YAML file,
which contains a dictionary, with one key for each attribute.

### Attribute metadata

The attribute metadata files contains a dictionary where each key is
a string - the attribute name - and each value is a dictionary -
the attribute metadata.

The following keys must be defined in each attribute metadata:
- ``definition``: a free text describing the attribute
- ``datatype``: the datatype of the attribute.

Thereby, the datatype shall be expressed as described in the
[datatypes section](https://github.com/ggonnella/attrtables/blob/main/docs/usage.md#datatype-description)
of the attrtables package documentation

Furthermore, the following keys can be defined:
- ``computation_group``: multiple attributes which are usually computed
together by plugins shall contain a common unique computation group
identifier in this field
- ``ontology_xref``: link to an ontology term, which defines the same attribute
- ``related_ontology_terms``: links to ontology terms, which do not directly
describe the attribute, but are related to its definition
- ``unit``: the measure unit for the attribute
- ``remark``: a free text remark

### Example

For example, a file ``basic_seqstats.yaml`` could contain:
```
gc_content:
  definition: fraction of the total bases of a sequence, which are G or C
  datatype: Float
  computation_group: basic_seqstats
seqlen:
  definition: seuqence length
  unit: bases
  datatype: Integer
  computation_group: basic_seqstats
```

The database can be prepared for storing the attributes defined in the file,
using:
```
prenacs-manage-attributes <dbuser> <dbpass> <dbname> <dbsocket> \
                      basic_seqstats.yaml
```

### Changing attribute metadata by constant datatype and computation group

If the ``datatype`` or ``computation_group`` of an attribute has not changed,
the ``prenacs-manage-attributes`` script can be run using the ``--update`` option.
This updates the attribute definition record.

For example, the metadata of GC content given in the previous section
could be given slightly differently in a file ``gc_content.yaml``:
```
gc_content:
  definition: portion of bases of a sequence, which are G or C
  datatype: Float
  computation_group: basic_seqstats
```

Since the ``definition`` changes, but not the ``datatype`` or
``computation_group``, this metadata could be used for updating the
``gc_content`` attribute record, as follows:
```
prenacs-manage-attributes <dbuser> <dbpass> <dbname> <dbsocket> \
                      --update gc_content.yaml
```

### Changing attribute metadata with different datatype and computation group

If the ``datatype`` or ``computation_group`` of an attribute has changed,
the attribute must be dropped from the database, before adding it again.
This means that the entire data for the attribute will be lost!
This can be achieved by running the ``prenacs-drop-attribute`` script.
After that, the attribute can be re-added by running
``prenacs-manage-attributes`` with the attribute definition file.

For example, the metadata of GC content given in the previous section
could be given with a different ``computation_group`` value
in a file ``seq_composition_stats.yaml``:
```
gc_content:
  definition: fraction of the total bases of a sequence, which are G or C
  datatype: Float
  computation_group: seq_composition_stats
```

If we want to use this definition, the existing data for GC content must be
destroyed, then the attribute definition is re-added, using:
```
# be careful: this deletes all the data for the attribute!
prenacs-drop-attribute <dbuser> <dbpass> <dbname> <dbsocket> gc_content
prenacs-manage-attributes <dbuser> <dbpass> <dbname> <dbsocket> \
                      seq_composition_stats.yaml
```

## Batch computing

The ``prenacs-batch-compute`` script is used for running a computation,
using a plugin. This assumes that the attributes computed by the plugin
have been added to the database, as explained in the previous section.
By default the computation is run in parallel, using the
``mutliprocessing`` module. If a serial computation is desired,
the ``--mode serial`` option can be used. If desired, the computation
can be run on a Slurm cluster (see below).

The batch compute function must locate the entities on which the
computation shall be run. The input entities can be provided as
a set of entity identifiers
can be provided as a list or in a column of a tabular file.
Alternatively a set of input files, one per entity, can be provided
(specified using a globpattern).
These different options are explained in the following sections.

For performance reasons, the computation results are not loaded directly
into the database and instead, they are first saved to a tabular file.
By default the results are output to the standard output, but the ``--out``
option can be used to specify a different file.
The first column contains the entity IDs. The following columns are the
results of the computation in the order specified by the plugin OUTPUT
constant. Note that each of the attribute can in some cases
include multiple columns.

Besides the attribute values, a computation report is output,
which contains the computation metadata in YAML format.
This file is necessary, in order to load the computation results
into the database. The output is by default to the standar error, but
a different file can be specified using the ``--report`` option.
Additional metadata for the report can be provided using further
options (see below).

Finally, a log file with additional information is output (by default to
the standard error, but a different file can be specified using
the ``--log`` option). This contains any further information about the
computation returned by the plugin ``compute`` function.
The output is tabular (tab-separated). The first column contains the
the entity IDs. The following columns contains the information
messages returned by the plugin. Each entity attribute computation
can generate zero, one or multiple lines.

## Running on a Slurm cluster

The computation can be run on a computer cluster managed by Slurm.
For this to work the ``prenacs-batch-compute`` script must be called
with the option ``--mode slurm``.

The user must provide, using the option ``--slurm-submitter <PATH_TO_SCRIPT>``
the path to a Bash script which is passed to the ``sbatch`` command.
An example is given in the library source code ``prenacs/submit_array_job.sh``, 
and this file should be used as a template.

Temporary files are used to perform a computation on a Slurm cluster. 
By default, these files are created in the current directory and 
removed after the computation is done. The directory of these files 
can be specified with the option ``--slurm-outdir``.

Slurm job arrays are utilized to perform computations for each task 
assigned to each input entity. If any of the tasks is failed, the ID of the relevant entity, 
the reason for the failure and the task ID in the Slurm job array 
are written to a tab-separated file named ``failed_tasks_{JOB_ID}.err``, 
where the JOB_ID corresponds to the Slurm job ID. If all tasks are failed, 
no such file is created, but the user is informed with a message.

Even if some tasks are failed, the results for the remaining completed tasks 
are still collected and reported in the output file. The user can then attempt 
to compute the failed tasks again using the information provided in the file 
``failed_tasks_{JOB_ID}.err``. This can be especially useful for jobs that require 
a large amount of computation but have few failed tasks for some reason. 

### Input entities provided as a set of identifiers

If the input entities are specified as a set of entity IDs, the ``ids``
subcommand of ``prenacs-batch-compute`` is used. In this case the filename of the
IDs file must be provided.

The file shall be either a list of entity IDs, with one ID per line, or a
tabular file, in which the entity IDs are contained in a column. In the second
case, the 1-based column number is also specified to ``prenacs-batch-compute``.

The IDs are passed to the plugin ``compute()`` function as argument, and are
used as first column of the output.

#### Computed entity IDs

It is possible also to use a list or tabular file is available,
containing IDs from which the entity IDs
can be computed, instead of the entity IDs themselves.

To achieve this, a module is created, which defines a
``compute_id(str)->str`` mapping function; the input of the function
is the ID provided in the ID list and the output is the entity ID.
The module filename is passed to ``batch_compute.py`` using the
``idsproc`` option.

### Input entities provided as a set of input files

If the input entities are provided as a set of files, the ``files`` subcommand
of ``prenacs-batch-compute`` is used.

The plugin ``compute()`` function of the plugin gets then the filename as
first argument.

In most cases, it is desirable to compute the entity IDs which shall be
used as a first column of the output.
To achieve this, a module is created, which defines a
``compute_id(str)->str`` mapping function; the input of the function
is the filename and the output is the entity ID to use in the output.
The module filename is passed to ``batch_compute.py`` using the
``idsproc`` option.

If no ``idsproc`` module is provided, the first column of the output
contains the input filename instead of an entity ID.

### Incremental computations

It is possible to automatically avoid the recomputation for entities,
for which a value has already been computed previously.

If a filename is provided using the ``--skip`` option, the entity IDs of
previous computations are read from the first column of this tabular file. If
the ID of an entity in the input (eventually after applying ``idsproc``) is
equal to one of the entity IDs of previous computations, then the computation
is skipped.

If the ``--out`` option is used and the output file already exists,
the existing output file is also used as ``--skip`` file.

### Computation parameters

The computation parameters can be provided to the plugin as a YAML file,
using the ``--params`` option.

The parameters are passed to the ``compute()`` function as keyword
arguments. The type and meaning of the parameters must be described
in the ``PARAMETERS`` constant of the plugin.

The computation parameters
are assumed to remain constant during the computation, i.e. the same
value is seen by each instance of ``compute()``.

If a parameter is called ``state``, it is handled in special way
(see next section). For this parameter, it is not assumed that the
value remains constant, and no description is necessary in the
``PARAMETERS`` plugin metadata constant.

### Computation state

Differently from the computation parameters, a computation state can be
defined. which possibly changes during the computation. When handling the
computation state, it shall be thereby considered that the computation
is run by default in parallel, using multiple processes.

The state is created by defining an``initialize()`` function in the plugin. The
function is run at the beginning of the batch computation and its return value
of ``initialize()`` is passed as keyword parameter ``state`` to the
``compute()`` function. If necessary, a ``finalize()`` function can be defined
by the plugin, which can perform teardown operations at the end of the batch
computation.

#### State initialization parameters

It is possible to provide parameters to the initialization function.
For this, a parameter in the file passed using the ``--params`` option
shall be named ``state``. This is handled in a special way: it is assumed
to be a dictionary with string keys. Its content is passed
to the ``initialize()`` function as keyword arguments.
The value of ``state`` is then overwritten by the return value of
``initialize()``.

### Report file metadata

The report file contains the username of the user starting the computation.
By default, this is computed using ``getpass.getuser()``. However a different
value can be provided using the ``--user`` option.

Furthermore, the name of the system on which the computation is run is added
to the report. By default, this is computed using ``socket.gethostname()``.
However, a different value can be provided using the ``--system`` option.

Optionally, the reason for the computation can be stated and added to the
report. The valid values for this are contained in the ``REASONS`` constants
of the ``Report`` class of the ``report.py`` module and are:
- ``new_entities``: the computation was run on entities, which did not exist
                    yet in the database
- ``new_attributes``: the computation was run on entities, which already existed
                      in the database, in order to compute new attributes
- ``recompute``: the computation was run on entities, which already existed in
                 the database, for attributes for which a value was already
                 computed before

## Loading the computation results

In order to load the results of the computation into the database, the
``prenacs-load-results`` script is used. To it the output files of
``prenacs-batch-compute`` (results and computation report) are passed.

The same plugin used for the batch computing must also be provided,
so that the plugin metadata can be stored in the database.

