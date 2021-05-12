import ast
import copy
import updator.astPatternBuilder as patternBuilder
from updator.astcompare import is_ast_like 


class AstConverter:
  """Scans Python code for AST nodes matching pattern.
  :param ast.AST pattern: The node pattern to search for
  """
  def __init__(self, rule, patternVars={}, assignRule=False):
    self.patternToSearch = rule.get("patternToSearch")
    self.patternToReplace = rule.get("patternToReplace")
    self.variables = patternVars

    if assignRule:
      self.assignmentPattern = rule["assignmentPattern"]

  def scan_ast(self, tree):
    """Walk an AST and replace nodes matching pattern for simple rule.
    :param ast.AST tree: The AST in which to search
    """
    patternSelf = self
    patternToSearch = self.patternToSearch
    patternToReplace = self.patternToReplace
    nodetype = type(patternToSearch)

    class convertTree(ast.NodeTransformer):
      def visit(self, node):
        ast.NodeVisitor.visit(self, node)

        if isinstance(node, nodetype) and is_ast_like(node, patternToSearch, patternSelf.variables):
          return patternSelf.getReplacedNode(patternToReplace, node)

        elif patternSelf.isInvalidNode(node):
          return None
        else:
          return node

    convertTree().visit(tree)

  def scan_ast_forAssignment(self, tree):
    """Walk an AST and replace nodes matching pattern for assignment rule.
    :param ast.AST tree: The AST in which to search
    """
    patternSelf = self
    patternToSearch = self.patternToSearch
    patternToReplace = self.patternToReplace
    assignmentPattern = self.assignmentPattern
    patternToSearchType = type(patternToSearch)
    assignPatternType = type(assignmentPattern)

    patternSelf.foundAssign = False

    class convertTree(ast.NodeTransformer):
      def visit(self, node):
        ast.NodeVisitor.visit(self, node)

        if isinstance(node, assignPatternType) and is_ast_like(node, assignmentPattern, patternSelf.variables, assignment=True):
          patternSelf.foundAssign = True

        if (isinstance(node, patternToSearchType) and 
            patternSelf.foundAssign and 
            is_ast_like(node, patternToSearch, patternSelf.variables, assignment=True)):

            return patternSelf.getReplacedNode(patternToReplace, node)

        elif patternSelf.isInvalidNode(node):
          return None
        else:
          return node

    convertTree().visit(tree)

  def getReplacedNode(self, patternToReplace, oldNode):
    if patternToReplace is not None and self.variables != {}:
      newNode = self.fillVariables(oldNode, patternToReplace)
      newNode = self.wrapToNewLine(newNode, oldNode)
      newNode = ast.copy_location(newNode, oldNode) # not sure it's needed
    else:
      newNode = patternToReplace

    return newNode

  def fillVariables(self, foundNode, patternToReplace):
    variables = self.variables
    patternSelf = self

    if variables == {}:
      return patternToReplace

    class RetransformPattern(ast.NodeTransformer):
      def visit_Name(self, node):
        if patternSelf.is_wildcard(node):
          return variables[node.id]
        else:
          return node

    patternToReplace = copy.deepcopy(patternToReplace)
    return RetransformPattern().visit(patternToReplace)

  def wrapToNewLine(self, newNode, oldNode):
    if (self.isNodeConsideredNewLine(oldNode) and 
      self.isNodeNotConsideredNewLine(newNode)):
      return ast.Expr(newNode)
    else:
      return newNode

  def isNodeConsideredNewLine(self, node):
    return type(node) in [ast.Assign]

  def isNodeNotConsideredNewLine(self, node):
    return type(node) in [ast.Call]

  def is_wildcard(self, nodePattern):
    return patternBuilder.is_wildcard(nodePattern)

  def isInvalidNode(self, node):
    return isinstance(node, ast.Expr) and self.isInvalidExpr(node)

  def isInvalidExpr(self, expNode):
    try:
      expNode.value
    except:
      return True

    return False
