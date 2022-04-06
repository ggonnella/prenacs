use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyclass] struct PythonConstants {}
#[pymethods]
impl PythonConstants {
  #[classattr] const ID:      &'static str = "rsecho";
  #[classattr] const VERSION: &'static str = "1.0";
  #[classattr] const INPUT:   &'static str = "anything";
  #[classattr] const OUTPUT: [&'static str; 1] = ["echo"];
  #[classattr] const ADVICE:  &'static str = "advice";
}

#[pyfunction]
fn compute(filename: &str) -> PyResult<String> {
  Ok(filename.to_string())
}

#[pymodule]
fn rust_changed_const_klass(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PythonConstants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}
