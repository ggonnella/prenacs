#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
import sys
from pathlib import Path
from glob import glob
from prenacs import plugins_helper, formatting_helper
from prenacs.report import Report
import tqdm
from concurrent.futures import as_completed, ProcessPoolExecutor
import multiplug

plugin=None

class EntityProcessor():
  @staticmethod
  def run(input_id, params):
    global plugin
    return plugin.compute(input_id, **params)

class BatchComputation():
  def __init__(self, plugin, verbose=False):
    """
    Initialize a batch computation instance based on a plugin.
    """
    self.plugin = multiplug.importer(plugin, verbose=verbose,
                                     **plugins_helper.COMPUTE_PLUGIN_INTERFACE)
    self.desc = formatting_helper.shorten(Path(plugin).stem, 15)
    self.state = None
    self.outfile = sys.stdout
    self.logfile = sys.stderr
    self.all_ids = None
    self.report = None
    self.params = {}
    self.computed = False

  def _compute_skip_set(self, skip_arg, verbose):
    skip = set()
    if skip_arg:
      if verbose:
        sys.stderr.write(f"# processing skip list... ({skip_arg})\n")
      with open(skip_arg) as f:
        for line in f: skip.add(line.rstrip().split("\t")[0])
      if verbose:
        sys.stderr.write("# done: skipping computation for "+\
                         f"up to {len(skip)} units\n")
    elif verbose:
      sys.stderr.write("# no skip list, all input units will be processed\n")
    return skip

  def _get_mod_function(self, filename, fun, verbose):
    if filename:
      pmod = multiplug.importer(filename, verbose=verbose,
                                **plugins_helper.IDPROC_PLUGIN_INTERFACE)
      return getattr(pmod, fun)
    else:
      return None

  def _compute_ids(self, unit_name, is_filename, idsproc):
    identifier = idsproc(unit_name) if idsproc else unit_name
    return (unit_name if is_filename else identifier), identifier

  def _input_units(self, globpattern, idsfile, idscol):
    if globpattern:
      return glob(globpattern)
    else:
      with open(idsfile) as f:
        return [line.rstrip().split("\t")[idscol-1] for line in f]

  def _compute_all_ids(self, globpattern, idsfile, idscol,
                       idsproc, skip, verbose):
    if verbose:
      sys.stderr.write("# compute input and output IDs...")
    result = []
    for unit_name in self._input_units(globpattern, idsfile, idscol):
      input_id, output_id = self._compute_ids(unit_name, globpattern, idsproc)
      if output_id in skip:
        skip.remove(output_id)
      else:
        result.append((input_id, output_id))
    if verbose:
      sys.stderr.write("done\n")
    return result

  def _select_input(self, globpattern=None, idsfile=None, idscol=None,
                  idsproc_module=None, skip=None, verbose=False):
    idsproc = self._get_mod_function(idsproc_module, "compute_id", verbose)
    skip = self._compute_skip_set(skip, verbose)
    self.all_ids = self._compute_all_ids(globpattern, idsfile, idscol,
                                         idsproc, skip, verbose)

  def input_from_globpattern(self, globpattern, idsproc_module=None,
                             skip=None, verbose=False):
    """
    Select the computation input using a glob pattern.

    # Input IDs

    The filename of each file in the glob pattern is used as the input
    ID passed to the plugin compute function.

    # Output IDs

    If a idsproc_module is specified, the ``compute_id`` function of
    the module is used to compute the output ID.
    Otherwise the filename is used also as the output ID.

    # Skip computation for some units

    A skip list file can be be defined using the parameter ``skip``.
    If skip is defined, then the computation is skipped for any
    output ID that is in the skip list.

    The skip list file can:
    - contain one output ID per line, or
    - be a tab-separated file with the output ID in the first column.
    """
    self._select_input(globpattern, None, None, idsproc_module, skip, verbose)

  def input_from_idsfile(self, idsfilename, idscol=1, idsproc_module=None,
                         skip=None, verbose=False):
    """
    Select the computation input using a tab-separated file.

    # Input IDs

    The entity IDs are passed as input to the plugin compute function.
    The IDs are obtained from the column specified by the parameter
    ``idscol`` (1-based column number) of the tab-separated file
    ``idsfilename``.

    If a idsproc_module is specified, the ``compute_id`` function of
    the module is used to compute the IDs from the column values.
    Otherwise the IDs are the column values themselves.

    # Output IDs

    The same IDs are used as input and output IDs.

    # Skip computation for some units

    A skip list file can be be defined using the parameter ``skip``.
    If skip is defined, then the computation is skipped for any
    ID that is in the skip list.

    The skip list file can:
    - contain one ID per line, or
    - be a tab-separated file with the ID in the first column.
    """
    if idscol < 1:
      raise ValueError("idscol must be a positive integer")
    self._select_input(None, idsfilename, idscol, idsproc_module, skip, verbose)

  def set_output(self, outfilename = None, logfilename = None):
    self.outfile = open(outfilename, "a") if outfilename else sys.stdout
    self.logfile = open(logfilename, "a") if logfilename else sys.stderr

  def setup_computation(self, params = {}, reportfile = sys.stderr,
                        user = None, system = None, reason = None,
                        verbose = False):
    """
    Setup the computation.

    It allows to set computation and report parameters and run
    the plugin initialization code.

    # Computation parameters

    Computation parameters are passed as a dictionary (``params``):
    - ``state``: a state object, which can change during the computation;
      it is passed to and/or setup by the initialization function of the plugin
      (see below)
    - any other key: any other parameter that the plugin may need
      and remains constant during the computation

    If no parameters are needed, then params can be omitted and defaults
    to an empty dictionary.

    ## Plugin initialization

    If the plugin has a ``initialize`` method, it is called.
    The return value of the ``initialize`` method is stored in the
    ``state`` parameter.

    If the parameter ``state`` was already defined, it is passed to the
    ``initialize`` method, and then overwritten with the return value of the
    ``initialize`` method.

    If a plugin initialization is not needed, then the plugin shall
    not define an ``initialize`` method.

    ## Report

    The following computation report parameters can be set:
    - ``reportfile`` sets the output file for the report (default: stderr)
    - ``user`` sets the user name for the report (default: system user
       as determined using ``getpass.getuser()``)
    - ``system`` sets the system name for the report (default: system
       name as determined using ``socket.gethostname()``)
    - ``reason`` sets the reason for the computation (default: undefined);
       it must be None or one of the reasons given in Report.REASONS

    If no report parameters are set, then the report is generated using
    the default values mentioned above.
    """
    if self.report:
      raise ValueError("Computation already set up")
    self.report = Report(reportfile, self.plugin,
                         user, system, reason, params)
    self.params = params
    if self.plugin.initialize is not None:
      self.params["state"] = \
          self.plugin.initialize(**self.params.get("state", {}))

  def _default_computation_setup(self):
    self.report = Report(sys.stderr, self.plugin)
    if self.plugin.initialize is not None:
      self.params["state"] = self.plugin.initialize()

  def _on_failure(self, output_id, exc):
    self.outfile.flush()
    self.logfile.flush()
    self.report.error(exc, output_id)

  def _on_success(self, output_id, results, logs):
    results = "\t".join([str(r) for r in results])
    if results:
      self.outfile.write(f"{output_id}\t{results}\n")
    for element in logs:
      if isinstance(element, list):
        for subelement in element:
          if subelement:
            self.logfile.write(f"{output_id}\t{subelement}\n")
      elif element:
        self.logfile.write(f"{output_id}\t{element}\n")
    self.report.step()

  def run(self, parallel=True, verbose=False):
    """
    Run the computation.

    By default, the computation is run in parallel
    (using a multiprocessing.Pool).
    Set parallel to False to run the computation serially.
    """
    if not self.all_ids:
      raise ValueError("Input was not selected")
    if not self.report:
      self._default_computation_setup()
    if parallel:
      self._run_in_parallel(verbose)
    else:
      self._run_serially(verbose)
    self.computed = True

  def _run_in_parallel(self, verbose):
    global plugin
    plugin = self.plugin
    entity_processor = EntityProcessor()
    if verbose:
      sys.stderr.write("# Computation will be in parallel (multiprocess)\n")
    with ProcessPoolExecutor() as executor:
      futures_map = {executor.submit(entity_processor.run,
                                     unit_ids[0], self.params):
                     unit_ids[1] for unit_ids in self.all_ids}
      for future in tqdm.tqdm(as_completed(futures_map), total=len(futures_map),
                              desc=self.desc):
        output_id = futures_map[future]
        try:
          results, *logs = future.result()
        except Exception as exc:
          self._on_failure(output_id, exc)
          raise(exc)
        else:
          self._on_success(output_id, results, logs)
    plugin = None

  def _run_serially(self, verbose):
    if verbose:
      sys.stderr.write("# Computation will be serial\n")
    for unit_ids in tqdm.tqdm(self.all_ids, desc=self.desc):
      output_id = unit_ids[1]
      try:
        results, *logs = self.plugin.compute(unit_ids[0], **self.params)
      except Exception as exc:
        self._on_failure(output_id, exc)
        raise(exc)
      else:
        self._on_success(output_id, results, logs)

  def finalize(self):
    """
    This method is called after the computation is finished.

    It finalizes the report, runs the plugin finalization code
    (if any) and closes the output files.
    """
    if not self.computed:
      raise ValueError("Computation not run")
    self.report.finalize()
    if self.plugin.finalize is not None:
      self.plugin.finalize(self.params.get("state", None))
    if self.outfile != sys.stdout: self.outfile.close()
    if self.logfile != sys.stderr: self.logfile.close()

