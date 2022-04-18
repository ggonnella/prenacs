#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy_repr import PrettyRepresentableBase
from sqlalchemy.dialects.mysql import BINARY

Base = declarative_base(cls=PrettyRepresentableBase)

utf8_cs_args = {'mysql_charset': 'utf8', 'mysql_collate': 'utf8_bin'}

class ComputationReport(Base):
  """
  Report of a computation.

  Tables storing the results of computations can refer to this table for the
  sake of data traceability and computation reproducibility.
  """
  __tablename__ = 'prenacs_computation_report'
  uuid = Column(BINARY(16), primary_key=True)
  plugin_id = Column(String(256), nullable=False)
  plugin_version = Column(String(64), nullable=False)
  parameters = Column(Text(4096))
  unit = Column(Enum("assembly"), nullable=False, default="assembly")
  n_units = Column(Integer, default=1)
  reason = Column(Enum("new_entities", "new_attributes", "recompute"))
  comp_status = Column(Enum("running", "completed", "partial", "aborted"),
                  nullable=False, default="running")
  system_id = Column(String(64))
  user_id = Column(String(64))
  time_start = Column(DateTime)
  time_end = Column(DateTime)
  used_resources = Column(Text(4096))
  remarks = Column(Text(4096))
  __table_args__ = utf8_cs_args

