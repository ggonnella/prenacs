use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyclass] struct Constants {}
#[pymethods]
impl Constants {
  #[classattr] const ID:      &'static str = "rsecho";
  #[classattr] const VERSION: &'static str = "1.0";
  #[classattr] const INPUT:   &'static str = "anything";
  #[classattr] const OUTPUT: [&'static str; 1] = ["echo"];
  #[classattr] const METHOD:  &'static str =
                     "echoes the input, for test purposes";
}

#[pyclass] struct State { count: u64 }

#[pyfunction]
fn initialize() -> PyRefMut<State> {
  let state = State { count: 1 };
  let gil = Python::acquire_gil();
  let py = gil.python();
  PyRefMut::new(py, State { count: 1}).unwrap()
}

#[pyfunction]
fn compute(filename: &str, state: PyRefMut<State>) -> PyResult<String> {
  Ok(filename.to_string())
}

#[pyfunction]
fn finalize(state: PyRefMut<State>) {
  let gil = Python::acquire_gil();
  let py = gil.python();
  println!("State is {}", state.as_ref(py).count);
}

#[pymodule]
fn rsecho(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Constants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(finalize, m)?)?;
    Ok(())
}
