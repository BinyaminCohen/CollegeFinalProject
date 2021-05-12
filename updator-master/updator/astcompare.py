"""Check Python ASTs against templates"""
import ast
import updator.astPatternBuilder as patternBuilder


def check_node_list(sample, template, assignment, variables, start_enumerate=0):
  """Check a list of nodes, e.g. function body"""
  if len(sample) != len(template):
    raise ASTMismatch(sample, template)

  for i, (sample_node, template_node) in enumerate(zip(sample, template), start=start_enumerate):
    if isinstance(template_node, ast.Name) and is_single_wildcard(template_node.id):
      treatWildcard(sample_node, variables, template_node.id, assignment)
    else:
      assert_ast_like(sample_node, template_node, variables, assignment)

def assert_ast_like(sample, template, variables, assignment):
  """Check that the sample AST matches the template.
  sample refers to source code tree.
  Raises a `ASTMismatch` if a difference is detected.
  """
  if not isinstance(sample, type(template)):
    raise ASTMismatch(sample, template)

  for name, template_field in ast.iter_fields(template):
    sample_field = getattr(sample, name)

    if isinstance(template_field, list):
      if template_field and isinstance(template_field[0], ast.AST):
        # if template_field[0].id is MULTIWILDCARD_NAME:
        if isinstance(template_field[0], ast.Name) and is_multi_wildcard(template_field[0].id):
          treatWildcard(sample_field, variables, template_field[0].id, assignment)
        else:
          check_node_list(sample_field, template_field, assignment, variables=variables)

      else:
        # List of plain values, e.g. 'global' statement names
        if sample_field != template_field:
          raise ASTMismatch(sample_field, template_field)

    elif isinstance(template_field, ast.AST):
      if isinstance(template_field, ast.Name) and is_single_wildcard(template_field.id):
        treatWildcard(sample_field, variables, template_field.id, assignment)

      else:
        assert_ast_like(sample_field, template_field, variables, assignment)
  
    else:
      # Single value, e.g. Name.id
      if sample_field != template_field and not is_single_wildcard(template_field):
        raise ASTMismatch(sample_field, template_field)

def is_wildcard(templateNode):
  return (isinstance(templateNode, ast.Name) and 
  patternBuilder.is_wildcard(templateNode))

def is_single_wildcard(templateNode):
  return patternBuilder.is_single_wildcard(templateNode)

def is_multi_wildcard(templateNode):
  return patternBuilder.is_multi_wildcard(templateNode)

def treatWildcard(nodesToSave, variables, wildcardName, assignment=False):
  existsNodes = variables.get(wildcardName)

  if assignment and existsNodes is not None:
    if not isVariablesEquals(existsNodes, nodesToSave):
      raise ASTMismatch(nodesToSave, existsNodes)
  else:
    variables[wildcardName] = nodesToSave

def isVariablesEquals(existsNodes, nodesToSave):
  return isNamesNodesEquals(existsNodes, nodesToSave) 

def isNamesNodesEquals(existsNodes, nodesToSave):
  return (isinstance(existsNodes, ast.Name) and 
  isinstance(nodesToSave, ast.Name) and
  existsNodes.id == nodesToSave.id)

def isAttrNodeEqualsToNameNode(existsNodes, nodesToSave):
  return ((isinstance(existsNodes, ast.Name) and 
  isinstance(nodesToSave, ast.Attribute) and
  existsNodes.id == nodesToSave.value.id))

def is_ast_like(sample, template, variables, assignment=False):
  """Returns True if the sample AST matches the template."""
  try:
    assert_ast_like(sample, template, variables, assignment)
    return True
  except ASTMismatch:
    return False

class ASTMismatch(AssertionError):
  """Exception for differing ASTs."""
  def __init__(self, got, expected):
    self.got = got
    self.expected = expected

  def __str__(self):
    return ("Mismatch - sample: " + self.got + ", template: " + self.expected)

