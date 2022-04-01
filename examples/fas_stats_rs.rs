use std::fs::File;
use std::io::Read;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use paste::paste;

// [dependencies] paste = "1.0"

#[pyclass] struct Constants {}
#[pymethods]
impl Constants {
  #[classattr] const ID:      &'static str = "fas_stats_rs";
  #[classattr] const VERSION: &'static str = "0.1.3";
  #[classattr] const INPUT:   &'static str = "genomic sequence (Fasta)";
  #[classattr] const OUTPUT: [&'static str; 2] = ["genome_size", "GC_content"];
  #[classattr] const METHOD:  &'static str = "count bases";
  #[classattr] const IMPLEMENTATION: &'static str =
                     "implemented in Rust, using a lookup table";
}

const BUFSIZE: usize = usize::pow(2, 16);

enum Location { InDesc, NewLine, InSeq }

macro_rules! define_construct_tab {
  ($i:ident, $($e:pat),+) => {
    paste! {
      const fn [<_construct_ $i:snake>]() -> [u64; 256] {
        let mut result: [u64; 256] = [0; 256];
        let mut i: u8 = 0;
        loop {
          match i as char {
            $($e => {result[i as usize] = 1})+
            _ => {}
          }
          i+=1;
          if i == 255 {break;}
        }
        result
      }
      const $i: [u64; 256] = [<_construct_ $i:snake>]();
    }
  }
}

define_construct_tab!(ISALPHATAB, 'a'..='z', 'A'..='Z');
define_construct_tab!(ISGCTAB, 'G', 'C', 'g', 'c');

fn process_buffer(location: &mut Location, n_read: usize,
                  buffer: &mut [u8], count1: &mut u64,
                  count2: &mut u64, tab1: [u64; 256],
                  tab2: [u64; 256]) {
  for i in 0..n_read {
    let c = buffer[i] as char;
    let n = buffer[i] as usize;
    match *location {
      Location::InDesc => { if c == '\n' {*location = Location::NewLine;} }
      Location::NewLine => {
        if c == '>' {*location = Location::InDesc;}
        else {
          *location = Location::InSeq;
          *count1 += tab1[n];
          *count2 += tab2[n];
        }
      }
      Location::InSeq => {
        if c == '\n' {*location = Location::NewLine;}
        else {
          *count1 += tab1[n];
          *count2 += tab2[n];
        }
      }
    }
  }
}

#[pyfunction]
fn compute(filename: &str) -> PyResult<(u64, f64)> {
  let mut f = File::open(filename).unwrap();
    let mut buffer = [0; BUFSIZE];
    let mut count_gc: u64 = 0;
    let mut count_alpha: u64 = 0;
    let mut location: Location = Location::InDesc;
    loop {
      let n_read = f.read(&mut buffer).unwrap();
      if n_read == 0 { break; } else {
        process_buffer(&mut location, n_read, &mut buffer, &mut count_alpha,
                       &mut count_gc, ISALPHATAB, ISGCTAB);
      }
    }
  Ok((count_alpha, count_gc as f64 / count_alpha as f64))
}

#[pymodule]
fn fas_stats_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Constants>()?;
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}
