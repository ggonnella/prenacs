import sys
from pathlib import Path
from glob import glob
from provbatch import plugins, formatting
from provbatch.reports import Report
import tqdm
from concurrent.futures import as_completed, ProcessPoolExecutor
import multiplug

class BatchComputation():
  def __init__(self, plugin, verbose=False):
    self.plugin = multiplug.importer(plugin, verbose=verbose,
                                     **plugins.COMPUTE_PLUGIN_INTERFACE)
    self.desc = formatting.shorten(Path(plugin).stem, 15)
    self.state = None
    self.outfile = sys.stdout
    self.logfile = sys.stderr
    self.all_ids = None
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
                                **plugins.IDPROC_PLUGIN_INTERFACE)
      return getattr(pmod, fun)
    else:
      return None

  def _compute_ids(self, unit_name, is_filename, idproc):
    identifier = idproc(unit_name) if idproc else unit_name
    return (unit_name if is_filename else identifier), identifier

  def _input_units(self, globpattern, idsfile, idscol):
    if globpattern:
      return glob(globpattern)
    else:
      with open(idsfile) as f:
        return [line.rstrip().split("\t")[idscol-1] for line in f]

  def _compute_all_ids(self, globpattern, idsfile, idscol,
                       idproc, skip, verbose):
    if verbose:
      sys.stderr.write("# compute input and output IDs...")
    result = []
    for unit_name in self._input_units(globpattern, idsfile, idscol):
      input_id, output_id = self._compute_ids(unit_name, globpattern, idproc)
      if output_id in skip:
        skip.remove(output_id)
      else:
        result.append((input_id, output_id))
    if verbose:
      sys.stderr.write("done\n")
    return result

  def select_input(self, globpattern=None, idsfile=None, idscol=None,
                  idproc_module=None, skip=None, verbose=False):
    idproc = self._get_mod_function(idproc_module, "compute_id", verbose)
    skip = self._compute_skip_set(skip, verbose)
    self.all_ids = self._compute_all_ids(globpattern, idsfile, idscol,
                                         idproc, skip, verbose)

  def set_output(self, outfilename = None, logfilename = None):
    self.outfile = open(outfilename, "a") if outfilename else sys.stdout
    self.logfile = open(logfilename, "a") if logfilename else sys.stderr

  def setup_computation(self, params = {}, report = None, user = None,
                        system = None, reason = None, verbose = False):
    if self.params:
      raise ValueError("Computation already set up")
    self.report = Report(report, self.plugin, user, system, reason, params)
    self.params = params
    if self.plugin.initialize is not None:
      self.params["state"] = \
          self.plugin.initialize(**self.params.get("state", {}))

  def _unit_processor(self, input_id):
    return self.plugin.compute(input_id, **self.params)

  def _on_failure(self, output_id, exc):
    self.outfile.flush()
    self.logfile.flush()
    self.report.error(exc, output_id)

  def _on_success(self, output_id, results, logs):
    results = "\t".join([str(r) for r in results])
    self.outfile.write(f"{output_id}\t{results}\n")
    if self.logfile and logs:
      for msg in logs:
        self.logfile.write(f"{output_id}\t{msg}\n")
    self.report.step()

  def run(self, parallel=True, verbose=False):
    if not self.all_ids:
      raise ValueError("Input was not selected")
    if not self.report:
      raise ValueError("Computation was not set up")
    if parallel:
      self._run_in_parallel(verbose)
    else:
      self._run_serially(verbose)
    self.computed = True

  def _run_in_parallel(self, verbose):
    if verbose:
      sys.stderr.write("# Computation will be in parallel (multiprocess)\n")
    with ProcessPoolExecutor() as executor:
      futures_map = {executor.submit(self._unit_processor, unit_ids[0]):
                     unit_ids[1] for unit_ids in self.all_ids}
      for future in tqdm.tqdm(as_completed(futures_map), total=len(futures_map),
                              desc=self.desc):
        output_id = futures_map[future]
        try:
          results, logs = future.result()
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
        results, logs = self.plugin.compute(unit_ids[0], **self.params)
      except Exception as exc:
        self._on_failure(output_id, exc)
        raise(exc)
      else:
        self._on_success(output_id, results, logs)

  def finalize(self):
    if not self.computed:
      raise ValueError("Computation not run")
    self.report.finalize()
    if self.plugin.finalize is not None:
      self.plugin.finalize(self.params.get("state", None))
    if self.outfile != sys.stdout: self.outfile.close()
    if self.logfile != sys.stderr: self.logfile.close()

