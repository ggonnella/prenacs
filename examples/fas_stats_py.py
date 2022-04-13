#
# (c) 2022 Giorgio Gonnella, University of Goettingen, Germany
#
##
## Compute simple sequence statistics for a Fasta file
##

ID =             "fas_stats_py"
VERSION =        "0.1.0"
INPUT =          "genome sequence (Fasta, optionally gzipped)"
OUTPUT =         ["genome_size", "GC_content"]
METHOD =         "count bases"
IMPLEMENTATION = "implemented in Python, using a lookup table"
PARAMETERS =     [("force_uncompressed", "bool", "false",
                        "do not use the zip library to open the input file")]

def compute(filename, **kwargs):
  gclen = 0
  seqlen = 0
  with open(filename) as f:
    for line in f:
      line = line.strip()
      if line[0] != ">":
        seqlen += len(line)
        for pos in range(len(line)):
          if line[pos] == 'C' or line[pos] == 'c' or \
             line[pos] == 'G' or line[pos] == 'g':
            gclen +=1
  return [seqlen, gclen/seqlen], []
