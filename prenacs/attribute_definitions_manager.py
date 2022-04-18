#
# (c) 2021-2022 Giorgio Gonnella, University of Goettingen, Germany
#
from sqlalchemy import select
from sqlalchemy.orm import Session
from prenacs.dbschema.attribute_definition import AttributeDefinition

class AttributeDefinitionsManager():

  def __init__(self, attribute_value_tables):
    self.avt = attribute_value_tables
    self.connection = attribute_value_tables.connectable

  def _check_invariant_column(self, adef, fname, fvalue):
    prev_value = getattr(adef, fname)
    if prev_value != fvalue:
      raise RuntimeError("Cannot update the definition of "+\
          f"attribute '{adef.name}' because changes in the column "+\
          f"{fname} are not allowed (previous value: "+\
          f"{prev_value}, current value: {fvalue})")

  def update(self, name, definition):
    """
    Update the definition of an attribute.

    The new definition must contain the same value as the previous definition
    for the keys "datatype" and "computation_group".

    All fields except "name", "datatype" and "computation_group" are updated.

    :param name: the name of the attribute
    :param definition: the new definition of the attribute, as a dictionary
    """
    session = Session(self.connection)
    select_adefs = select(AttributeDefinition).where(\
        AttributeDefinition.name == name)
    adef = session.execute(select_adefs).scalars().first()
    if adef is None:
      raise RuntimeError("Cannot update the definition of attribute "+\
          f"'{name}' because it does not exist")
    for fname, fvalue in definition.items():
      if fname in ["datatype", "computation_group"]:
        self._check_invariant_column(adef, fname, fvalue)
      else:
        setattr(adef, fname, fvalue)
    session.add(adef)
    session.commit()

  def update_changed(self, definitions):
    """
    Update the definitions of attributes given in a dictionary
    that are different from the values in the database.

    :param definitions: dictionary containing the attribute name as keys and the
                        other definition columns as values

    If an attribute given in the dictionary does not exist in the
    database, or if exists, but it is unchanged, it is ignored.
    """
    if definitions:
      session = Session(self.connection)
      select_adefs = select(AttributeDefinition)
      for adef in session.execute(select_adefs).scalars().all():
        if adef.name in definitions:
          for fname, fvalue in definitions[adef.name].items():
            if fname in ["datatype", "computation_group"]:
              self._check_invariant_column(adef, fname, fvalue)
            else:
              setattr(adef, fname, fvalue)
          session.add(adef)
      session.commit()

  def drop(self, name):
    """
    Drop an attribute from the database.

    :param name: the name of the attribute to drop
    """
    self.avt.destroy_attribute(name)

  def drop_missing(self, definitions):
    """
    Drop attributes that are not in the definitions.

    :param definitions: dictionary containing the attribute name as keys and the
                        other definition columns as values

    If an attribute present in the database does not exist in the
    definitions dictionary, it is removed from the database.

    Note that all values for the attribute are lost!
    """
    for aname in self.avt.attribute_names:
      if not definitions or aname not in definitions:
        self.avt.destroy_attribute(aname)

  def insert(self, name, definition):
    """
    Insert a new attribute into the database.

    :param name: the name of the attribute to insert
    :param definition: the definition of the attribute, as a dictionary
    """
    self.avt.create_attribute(name, **definition)

  def insert_new(self, definitions):
    """
    Insert in the database attributes from the definitions
    that are not yet in the database.

    :param definitions: dictionary containing the attribute name as keys and the
                        other definition columns as values

    If an attribute already exists in the database, it is ignored.
    """
    if definitions:
      for aname, adef in definitions.items():
        if aname not in self.avt.attribute_names:
          self.avt.create_attribute(aname, **adef)

  def apply_definition(self, aname, definition):
    if aname not in self.avt.attribute_names:
      self.avt.create_attribute(aname, **definition)
    else:
      self.update(aname, definition)

  def apply_definitions(self, definitions, drop_missing=True,
                        insert_new=True, update_changed=True):
    if drop_missing:   self.drop_missing(definitions)
    if insert_new:     self.insert_new(definitions)
    if update_changed: self.update_changed(definitions)
