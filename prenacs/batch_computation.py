#
# (c) 2021-2023 Giorgio Gonnella, University of Goettingen, Germany
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
import os
import shutil
import sh

class EntityProcessor():
  """
  A class that processes entities using a dumped plugin compute.

  Attributes:
    dumped_plugin_compute (bytes): The dumped plugin compute.

  Methods:
    run(input_id, params): Runs the plugin compute on the given input ID
                           and parameters.
  """

  def __init__(self, dumped_plugin_compute):
    self.dumped_plugin_compute = dumped_plugin_compute

  def run(self, input_id, params):
    """
    Runs the plugin compute on the given input ID and parameters.

    Args:
      input_id (str): The input ID.
      params (dict): The parameters to pass to the plugin compute.

    Returns:
      Any: The output of the plugin compute.
    """
    plugin_compute = dill.loads(self.dumped_plugin_compute)
    return plugin_compute(input_id, **params)

class BatchComputation():
  """
  A class that performs batch computation of entities using a plugin.

  Attributes:
    Plugin:
      plugin (str): The path to the plugin to use for computation.
      desc (str): A shortened description of the plugin.

    Input/Output data:
      all_ids (list): The input and output IDs for all input units.

    Computation parameters/results:
      params (dict): The parameters to pass to the plugin compute.
      state (str): The current state of the computation.
      report (Report): The report object for the computation.
      computed (bool): Whether the computation has been performed.

    Output control:
      verbose (bool): Whether to print verbose output.

    File handles:
      outfile (file): The file to write output to.
      logfile (file): The file to write log messages to.

    Slurm-specific attributes:
      slurmoutdir (str): The path to the SLURM output directory.
      slurmtmpdir (str): The path to the SLURM temporary directory.
  """

  def __init__(self, plugin, verbose=False):
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
    self.slurmoutdir = None
    self.slurmtmpdir = None

  def _compute_skip_set(self, skip_arg, verbose):
    skip = set()
    if skip_arg and os.path.exists(skip_arg):
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

  def set_slurm_params(self, pluginfilename, submitterfilename,
                      outdirname = None):
    self.slurmsubmitter = Path(submitterfilename)
    self.slurmoutdir = Path(outdirname) \
        if outdirname else Path("prenacs_slurm_out")
    Path(self.slurmoutdir).mkdir(parents=True, exist_ok=True)
    self.slurmtmpdir = tempfile.mkdtemp(prefix="prenacs", suffix="temp",
                                        dir=self.slurmoutdir)
    self.plugin_f = Path(pluginfilename)

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

  def run(self, mode="parallel", verbose=False):
    """
    Run the computation.

    By default, the computation is run in parallel
    (using a multiprocessing.Pool).

    Other modes are:
    - serial: run the computation serially
    - slurm: run on a computer cluster managed by Slurm
    """
    if not self.all_ids:
      if verbose:
        sys.stderr.write("# Warning: no computation, input list is empty\n")
    if not self.report:
      self._default_computation_setup()
    if mode == "slurm":
      self._run_on_slurm_cluster(verbose)
    elif "parallel":
      self._run_in_parallel(verbose)
    elif "serial":
      self._run_serially(verbose)
    else:
      raise RuntimeError(f"The computation mode '{mode}' is unknown\n"+\
                        "It must be one of: parallel, serial, slurm.")
    self.computed = True

  def _run_on_slurm_cluster(self, verbose):
    if verbose:
      sys.stderr.write("# Computation will be on a SLURM cluster\n")
    with tempfile.NamedTemporaryFile(delete=False, mode="wb",
                                     dir=self.slurmtmpdir) as params_f:
      dill.dump(self.params, params_f)
    with tempfile.NamedTemporaryFile(delete=False, mode="wb",
                                     dir=self.slurmtmpdir) as input_list_f:
      dill.dump([i[0] for i in self.all_ids], input_list_f)

    # Remove the output and temporary folders
    def _remove_slurm_dirs():
      shutil.rmtree(self.slurmoutdir)

    # Run the sbatch script with given parameters and get the job id
    array_len = len(self.all_ids)
    if array_len == 0:
      sys.stderr.write("# Job array is empty! Computation could not start! "+\
          "Have you already performed the computation for these units?\n")
      _remove_slurm_dirs()
      sys.exit(1)
    else:
      sys.stderr.write(f"# Number of tasks in the job array: {array_len}\n")
    try:
      sbatch_out = sh.sbatch("--parsable", "-a", f"0-{array_len-1}",
                              str(self.slurmsubmitter),
                              str(self.plugin_f),
                              str(params_f.name),
                              str(input_list_f.name),
                              str(self.slurmoutdir),
                              _piped="err")
      job_id = [int(i) for i in str(sbatch_out).split(";") \
          if i.strip().isdigit()][0]
    except sh.ErrorReturnCode:
      _remove_slurm_dirs()
      raise ValueError("# Job submission is unsuccessful!\n")
    except Exception as exc:
      _remove_slurm_dirs()
      raise exc
    else:
      sys.stderr.write("# Job submission is successful. "+\
          f"Slurm job id: {job_id}\n")

    def _get_stats(job_id):
      stats_dict = {}
      stats_out = str(sh.sacct("-n", "-X", "-j", f"{job_id}", "-o",
                               "jobid,state%20")).split("\n")
      for stat in stats_out:
        s_pair = stat.split()
        s_id, s_desc = None, None
        if len(s_pair) == 2:
          last_char = s_pair[0].split(f"{job_id}_")[-1]
          if last_char.isdigit():
            s_id = int(last_char)
          s_desc = s_pair[1]
          if s_desc and s_id is not None:
            if s_desc not in stats_dict:
              stats_dict[s_desc] = []
            stats_dict[s_desc].append(s_id)
      if stats_dict:
        sys.stderr.write("------------------\n")
        for status in stats_dict:
          sys.stderr.write(f"# {status}: {len(stats_dict[status])}\n")
        sys.stderr.write("------------------\n")
      else:
        sys.stderr.write("# Job status cannot be retrieved at the moment!")
      return stats_dict

    # Report the status of each job
    n_completed = 0
    progress_bar = tqdm.tqdm(total=array_len, ascii=True)
    while int(sh.wc(sh.squeue("--jobs", f"{job_id}"), "-l")) > 1:
      sleep(5)
      stats_dict = _get_stats(job_id)
      n_completed = len(stats_dict.get("COMPLETED", []))
      progress_bar.n = n_completed
      progress_bar.refresh()
      sleep(10)

    # Check if any of the tasks has been completed
    # If so, collect the results into the output file
    # If some tasks are failed, write the status of
    # each uncompleted task into a tsv file
    stats_dict = _get_stats(job_id)
    n_completed = len(stats_dict.get("COMPLETED", []))
    if progress_bar.n != n_completed:
      progress_bar.n = n_completed
      progress_bar.refresh()
    progress_bar.close()
    if n_completed > 0:
      if n_completed == array_len:
        sys.stderr.write("# All tasks have been completed successfully!\n")
      else:
        err_f = f"failed_tasks_{job_id}.err"
        with open(err_f, "a") as f:
          for status in stats_dict:
            if status != "COMPLETED":
              for i in stats_dict[status]:
                f.write(f"{self.all_ids[i][1]}\t{status}\t{i}\n")
        sys.stderr.write(f"# {array_len-n_completed} tasks have "+\
            "NOT been completed!\n")
        sys.stderr.write(f"# You can find the details about the "+\
            "uncompleted tasks in the file named {err_f}\n")
      for out_f in glob(f"{self.slurmoutdir}/*"):
        f_name = Path(out_f).stem
        if f_name.isdigit():
          f_id = int(f_name)
          output_id = self.all_ids[f_id][1]
          with open(out_f, "rb") as f:
            results, *logs = dill.load(f)
            self._on_success(output_id, results, logs)
    else:
      sys.stderr.write("# All tasks have failed!\n")

    # Remove the output and temporary folder
    _remove_slurm_dirs()

  def _run_in_parallel(self, verbose):
      entity_processor = EntityProcessor(dill.dumps(self.plugin.compute))
      if verbose:
        sys.stderr.write("# Computation will be in parallel (multiprocess)\n")
      with ProcessPoolExecutor() as executor:
        futures_map = {executor.submit(entity_processor.run,
                                       unit_ids[0], self.params):
                       unit_ids[1] for unit_ids in self.all_ids}
        for future in tqdm.tqdm(as_completed(futures_map),
                                total=len(futures_map), desc=self.desc):
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

