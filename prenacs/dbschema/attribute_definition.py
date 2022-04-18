#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#

"""
DB Schema for tables storing attribute values.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text
from sqlalchemy_repr import PrettyRepresentableBase

Base = declarative_base(cls=PrettyRepresentableBase)

utf8_cs_args = {'mysql_charset': 'utf8', 'mysql_collate': 'utf8_bin'}

class AttributeDefinition(Base):
  """
  Describes an assembly attribute.

  If no definition is provided, the definition is given by the
  ontology link; otherwise the ontology link is a term which is
  related to the definition, in a way described in the definition.
  """
  __tablename__ = "prenacs_attribute_definition"
  name = Column(String(62), primary_key=True)
  datatype = Column(String(256), nullable=False)
  definition = Column(Text(4096))
  ontology_xref = Column(String(64))
  related_ontology_terms = Column(Text(4096))
  unit = Column(String(64))
  remark = Column(Text(4096))
  computation_group = Column(String(62), index=True)
  __table_args__ = utf8_cs_args

