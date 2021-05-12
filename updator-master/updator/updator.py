import ast
import astor
import click
import os.path
import os
from tabulate import tabulate
import updator.astPatternBuilder as patternBuilder
from updator.dbInterface import DbInterface
from updator.fsInterface import FsInterface
from updator.astConverter import AstConverter


def findModuleAlias(tree, moduleName):
  class AliasFinder(ast.NodeVisitor):

    def __init__(self, moduleName):
      super(AliasFinder, self).__init__()
      self.moduleName = moduleName
      self.aliasModuleName = None

    def visit_alias(self, node):
      if (node.name == self.moduleName and node.asname is not None):
        self.aliasModuleName = node.asname
      elif (node.name == self.moduleName and node.asname is None):
        self.aliasModuleName = node.name

    def get_found_alias(self):
      return self.aliasModuleName

  class ImportFinder(ast.NodeVisitor):
    def __init__(self, moduleName):
      super(ImportFinder, self).__init__()
      self.moduleName = moduleName;
      self.aliasFinderClass = AliasFinder(self.moduleName)

    def visit_Import(self, node):
      self.aliasFinderClass.visit(node)

    def get_found_alias(self):
      return self.aliasFinderClass.get_found_alias()

  aliasFinderClass = ImportFinder(moduleName)
  aliasFinderClass.visit(tree)
  return aliasFinderClass.get_found_alias()

def applyRule(rule, module, tree):
  assignmentRule = rule.get("assignmentRule")

  if assignmentRule:
    applyAssignmentRule(rule, module, tree, assignmentRule)

  if (assignmentRule is None) or (assignmentRule == "auto"):
    patternVars = {}
    
    rule = patternBuilder.prepareRule(rule, module)
    astConverter = AstConverter(rule, patternVars)
    
    astConverter.scan_ast(tree)

def applyAssignmentRule(rule,  module, tree, assignmentType):
  assignmentRule = patternBuilder.createAssignmentRule(rule, module, assignmentType)
  patternVars = {}

  astConverter = AstConverter(assignmentRule, patternVars, assignRule=True)
  astConverter.scan_ast_forAssignment(tree)

def showRules(dbInterface, lib):
  rules = dbInterface.findAllRulesByLib(lib)
  rules = list(map(lambda r: [r["patternToSearch"], r["patternToReplace"], r.get("assignmentPattern"), r.get("assignmentRule"), r["active"]], rules))

  if rules == []:
    print("library '" + lib + "' does not exists.")
  else:
    print("Rules for '" + lib + "' library: \n")
    print(tabulate(rules, headers=["id", "patternToSearch", "patternToReplace", "assignmentPattern", "hasAssignmentType", "active"], showindex="always"))

  return rules

def isRuleValid(rule, lib, assignmentType):
  try:
    if assignmentType:
      patternBuilder.createAssignmentRule(rule, lib, assignmentType)
    else:
      patternBuilder.prepareRule(rule, lib)
    return True
  except Exception as e:
    return False

def createRule(rule, assignmentType, assignmentPattern, property):
  if assignmentType:
    rule["assignmentRule"] = assignmentType

  if assignmentPattern:
    rule["assignmentPattern"] = assignmentPattern

  if property:
    rule["property"] = property

  return rule

@click.group()

def main():
  """Automatically upgrade python libraries"""

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
@click.argument('path', metavar="path", type=click.Path(exists=True))

def run(lib, path):
  """execute updator to apply the upgrade"""
  fsInterface = FsInterface()
  dbInterface = DbInterface()

  sourceCode = fsInterface.readFileSourceCode(path)
  tree = ast.parse(sourceCode)
  moduleAlias = findModuleAlias(tree, lib)

  if moduleAlias is None:
    return

  rules = dbInterface.findRulesByLib(lib)

  for rule in rules:
    applyRule(rule, moduleAlias, tree)

  convertedCode = astor.to_source(tree)
  fsInterface.saveConvertedCode(path, convertedCode)
  print("updator upgraded '" + lib + "' lib successfully.")

@main.command()
def show_libs():
  """show list of libraries"""
  dbInterface = DbInterface()
  libs = dbInterface.findLibs()
  libs = map(lambda l: [l["_id"], l["count"]], libs)
  print(tabulate(list(libs), headers=["library", "rules count"]))

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def show_rules(lib):
  """show list of rules of a certain library"""
  dbInterface = DbInterface()
  showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def deactivate_rule(lib):
  """deactivate rule of a certain library"""
  dbInterface = DbInterface()
  rules = showRules(dbInterface, lib)
  if rules != []:
    choices= [str(i) for i in range(len(rules))]
    id = click.prompt("Chose rule id to deactivate", type=click.Choice(choices), confirmation_prompt=True)
    dbInterface.deactivateRule({"module": lib, "patternToSearch": rules[int(id)][0]})
    print("\nDeactivate rule id (" + id + ") successfully.")
    showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def reactivate_rule(lib):
  """reactivate rule of a certain library"""
  dbInterface = DbInterface()
  rules = showRules(dbInterface, lib)
  if rules != []:
    choices= [str(i) for i in range(len(rules))]
    id = click.prompt("Chose rule id to reactivate", type=click.Choice(choices), confirmation_prompt=True)
    dbInterface.reactivateRule({"module": lib, "patternToSearch": rules[int(id)][0]})
    print("\nReactivate rule id (" + id + ") successfully.")
    showRules(dbInterface, lib)

@main.command()
@click.argument('lib', metavar="lib", type=click.STRING)
def add_rule(lib):
  """add rule to a certain library"""
  assignmentChoices = ["auto", "manual"]
  assignmentType = click.prompt("Chose a type of assignment rule or (empty enter to none)", default=False, type=click.Choice(assignmentChoices))
  assignmentPattern = None
  property = None

  if assignmentType:
    if assignmentType == "manual":
      assignmentPattern = click.prompt("Enter pattern of assignment", type=click.STRING)
    elif assignmentType == "auto":
      property = click.prompt("Enter the property to which the change applies", type=click.STRING)

  patternToSearch = click.prompt("Enter pattern to search", type=click.STRING)
  patternToReplace = click.prompt("Enter pattern to replace", type=click.STRING)
  click.confirm("Do you confirm?", abort=True)

  base_rule = {
    "module": lib,
    "patternToSearch": patternToSearch,
    "patternToReplace": patternToReplace
  }

  rule = createRule(base_rule, assignmentType, assignmentPattern, property)

  if isRuleValid(rule, lib, assignmentType):
    DbInterface().insertRule(rule)
    print("Inserted given rule successfully.")
  else:
    print("Given rule patterns are not valid.")


if __name__ == '__main__':
  main()
