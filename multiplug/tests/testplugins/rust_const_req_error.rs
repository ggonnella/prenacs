use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyclass] struct Constants {}
#[pymethods]
impl Constants {
  #[classattr] const ID:      &'static str = "rsecho";
  #[classattr] const VERSION: &'static str = "1.0";
  #[classattr] const INPUT:   &'static str = "anything";
  #[classattr] const METHOD:  &'static str =
                     "echoes the input, for test purposes";
}

#[pyfunction]
fn compute(filename: &str) -> PyResult<String> {
  Ok(filename.to_string())
}

#[pymodule]
fn rust_const_req_error(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Constants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}
