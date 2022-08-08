#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
import sys
from pathlib import Path
from glob import glob
from time import sleep
from prenacs import plugins_helper, formatting_helper
from prenacs.report import Report
import tqdm
from concurrent.futures import as_completed, ProcessPoolExecutor
import multiplug
import tempfile
import dill
import sh

class EntityProcessor():

  def __init__(self, dumped_plugin_compute):
    self.dumped_plugin_compute = dumped_plugin_compute

  def run(self, input_id, params):
    plugin_compute = dill.loads(self.dumped_plugin_compute)
    return plugin_compute(input_id, **params)

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

  def run(self, parallel=True, verbose=False, slurm=False):
    """
    Run the computation.

    By default, the computation is run in parallel
    (using a multiprocessing.Pool).
    Set parallel to False to run the computation serially.
    """
    if not self.all_ids:
      if verbose:
        sys.stderr.write("# Warning: no computation, input list is empty\n")
    if not self.report:
      self._default_computation_setup()
    if slurm:
      self._run_on_slurm_cluster(verbose)
    elif parallel:
     self._run_in_parallel(verbose)
    else:
     self._run_serially(verbose)
    self.computed = True

  def _run_on_slurm_cluster(self, verbose):
    temp_dir = Path().absolute()/"tmp" # This should be determined by the user
    temp_dir.mkdir(parents=True, exist_ok=True)
    if verbose:
      sys.stderr.write("# Computation will be on a SLURM cluster\n")
    with tempfile.NamedTemporaryFile(delete=False, mode="wb", dir=temp_dir) as params_f:
      dill.dump(self.params, params_f)
    with tempfile.NamedTemporaryFile(delete=False, mode="wb", dir=temp_dir) as input_list_f:
      dill.dump([i[0] for i in self.all_ids], input_list_f)
    
    # Run the sbatch script with given parameters and get the job id
    plugin_f = self.plugin.__file__  # Is there a better way to get the path?
    submit_f = Path(__file__).parent.absolute()/"submit_array_job.sh"
    array_len = len(self.all_ids)
    output_dir = Path().absolute()/"out" # Tentatively describe an output directory for testing
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
      sbatch_out = sh.sbatch("--parsable", "-a", "0-{}".format(array_len-1),
                              str(submit_f),
                              str(plugin_f),
                              str(params_f.name),
                              str(input_list_f.name),
                              str(output_dir))
      job_id = [int(i) for i in str(sbatch_out).split(";") if i.strip().isdigit()][0]
    except sh.ErrorReturnCode:
      raise ValueError("Job submission is unsuccessful!\n")
    except Exception as exc:
      raise(exc)
    else:
      sys.stderr.write("# Job submission is successful\n")
      
    # Get the job statistics with sacct command
    def _get_stats(job_id):
      stats_dict = {}
      stats_out = str(sh.uniq(sh.sort(sh.sacct("-n", "-X", "-j", "{}".format(job_id), "-o", "state%20")), "-c")).split("\n")
      for stat in stats_out:
        s_pair = stat.split()
        s_desc, s_int = None, None
        if len(s_pair) == 2:
          for p in s_pair:
            if p.isdigit():
             s_int = int(p)
            else:
              s_desc = p
          if s_desc is not None and s_int is not None:
            stats_dict[s_desc] = s_int
          else:
            sys.stderr.write("# Job status cannot be retrieved at the moment!\n")
      if stats_dict:
        for k in stats_dict:
          sys.stderr.write("# {}: {}\n".format(k, stats_dict[k]))
        if "COMPLETED" in stats_dict:
          n_completed = stats_dict["COMPLETED"]
          progress_bar.n = n_completed
          progress_bar.refresh()
      return stats_dict      

    # Report the status of each job    
    n_completed_jobs = 0
    progress_bar = tqdm.tqdm(total=array_len)
    while int(sh.wc(sh.squeue("--jobs", "{}".format(job_id)), "-l")) > 1:
      sleep(5)
      _get_stats(job_id)
      sleep(15)
    
    # Check if all jobs have been completed
    stats_dict = _get_stats(job_id)
    n_completed = stats_dict.get("COMPLETED", 0)
    if n_completed == array_len:
      sys.stderr.write("# All jobs have been completed successfully!\n")
    else:
      sys.stderr.write("# {} jobs have failed!\n".format(array_len-n_completed))
    progress_bar.close()
    
    # Go into the output folder and collect the results
    for out_f in glob(f"{output_dir}/*"):
      f_name = Path(out_f).stem
      if f_name.isdigit():
        f_id = int(f_name) 
        output_id = self.all_ids[f_id][1]
        with open(out_f, "rb") as f:
          results, *logs = dill.load(f)
          self._on_success(output_id, results, logs)

  def _run_in_parallel(self, verbose):
    entity_processor = EntityProcessor(dill.dumps(self.plugin.compute))
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

