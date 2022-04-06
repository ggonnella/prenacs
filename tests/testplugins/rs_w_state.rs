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
fn initialize() -> PyResult<Py<State>> {
  let gil = Python::acquire_gil();
  let py = gil.python();
  let state = Py::new(py, State { count: 0 })?;
  eprintln!("initialized state, count=0");
  Ok(state)
}

#[pyfunction]
fn compute(filename: &str, state: Py<State>) -> PyResult<String> {
  let gil = Python::acquire_gil();
  let py = gil.python();
  let mut state = state.borrow_mut(py);
  state.count += 1;
  eprintln!("count={}", state.count);
  Ok(filename.to_string())
}

#[pyfunction]
fn finalize(state: Py<State>) {
  let gil = Python::acquire_gil();
  let py = gil.python();
  let mut state = state.borrow_mut(py);
  state.count += 1;
  eprintln!("finalized state, count={}", state.count);
}

#[pymodule]
fn rs_w_state(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Constants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(finalize, m)?)?;
    Ok(())
}
