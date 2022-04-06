use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyclass] struct Constants {}
#[pymethods]
impl Constants {
  #[classattr] const ID:      &'static str = "rsecho";
  #[classattr] const VERSION: &'static str = "1.0";
  #[classattr] const INPUT:   &'static str = "anything";
  #[classattr] const OUTPUT: [&'static str; 1] = ["echo"];
  #[classattr] const ADVICE:  &'static str = "advice";
  #[classattr] const UNDECLARED_CONST:  &'static str = "imported";
}

#[pyfunction]
fn initialize() -> PyResult<String> {
  Ok("init".to_string())
}

#[pyfunction]
fn compute(filename: &str) -> PyResult<String> {
  Ok(filename.to_string())
}

#[pyfunction]
fn undeclared_func() -> PyResult<String> {
  Ok("imported".to_string())
}

#[pymodule]
fn rust_no_req_error(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Constants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(undeclared_func, m)?)?;
    Ok(())
}
