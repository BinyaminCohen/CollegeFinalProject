import sys
import unittest
import textwrap
import traceback
from updator.dbInterface import DbInterface
from updator.updator import main
from click.testing import CliRunner


fileToConvert = "./tests/codeFileToConvert.py"

class UpdatorTests(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(UpdatorTests, self).__init__(*args, **kwargs)
    self.dbInterface = DbInterface()
    self.cliRunner = CliRunner()

  def setUp(self):
    print(self._testMethodName)
    self.dbInterface.dropRules()

  def insertRule(self, rule):
    self.dbInterface.insertRule(rule)

  def updatorRun(self, lib, fileToConvert):
    result = self.cliRunner.invoke(main, ["run", lib, fileToConvert])
    if result.output is not "":
      print(result.output)
    if result.exit_code is not 0 and result.exc_info is not None:
      print(result.exc_info[0])
      print(result.exc_info[1])
      traceback.print_tb(result.exc_info[2])

  def createCodeFile(self, codeText):
    with open(fileToConvert, 'w') as f:
      f.write(textwrap.dedent(codeText))
      f.close()

  def readCodeFile(self):
    with open(fileToConvert, 'r') as f:
      codeContent = f.read()
      f.close()

      return codeContent

  def dropWhitespace(self, str):
    return ''.join(str.split()) 

class UpdatorGenericTests(UpdatorTests):
  def setUpClass(self):
    print("---------------------")
    print("Updator genric tests")
    print("---------------------")

  def test_module_name_unused_in_source_code(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    rule = { "module": "math", 
             "patternToSearch": "math.pow($_)", 
             "patternToReplace": "math.pow2($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    moduleName = "sys"
    self.updatorRun(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_module_name_with_alias(self):
    sourceCode = '''
      import math as m
      x = 2
      y = 3
      m.pow(x, y)     
    '''

    expectedConvertedCode = '''
      import math as m
      x = 2
      y = 3
      m.pow2(x, y)     
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($_)", 
             "patternToReplace": "math.pow2($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    moduleName = "math"
    self.updatorRun(moduleName, fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RenameFunctionTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Rename function tests")
    print("-------------------------------")

  def test_rename_function_without_params(self):
    sourceCode = '''
      import os
      os.remove()        
    '''

    expectedConvertedCode = '''
      import os
      os.delete()        
    '''

    rule = { "module": "os", 
             "patternToSearch": "os.remove()", 
             "patternToReplace": "os.delete()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_destructure_each_function_params_to_wildcard(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir', 'binyamin')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2)", 
         "patternToReplace": "os.delete($1, $2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_destructure_all_params_to_wildcard(self):
    sourceCode = '''
      import os as s
      s.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os as s
      s.delete('shir', 'binyamin')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_function_and_change_params_order(self):
    sourceCode = '''
      import os as s
      s.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os as s
      s.delete('binyamin', 'shir')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2)", 
         "patternToReplace": "os.delete($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_without_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    rule = { "module": "math", 
         "patternToSearch": "math.pow()", 
         "patternToReplace": "math.pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_with_too_many_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    rule = { "module": "math", 
         "patternToSearch": "math.pow($1, $2, $3)", 
         "patternToReplace": "math.pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_pattern_to_search_should_not_be_found_case_pattern_has_not_enough_params(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = sourceCode

    rule = { "module": "math", 
         "patternToSearch": "math.pow($1)", 
         "patternToReplace": "math.pow2()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_multiwildcard_should_match_func_without_params(self):
    sourceCode = '''
      import os
      os.remove()
    '''

    expectedConvertedCode = '''
      import os
      os.delete()
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_without_params_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove())
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete())
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_inner_func_with_params(self):
    sourceCode = '''
      import os
      os.remove(os.remove('shir', 'binyamin'))
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete('shir', 'binyamin'))
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_outter_func_with_3_params(self):
    sourceCode = '''
      import os
      os.remove(2, os.remove('shir'), 1)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(2, os.delete('shir'), 1)
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_when_inner_pattern_exists_twice(self):
    sourceCode = '''
      import os
      os.remove(os.remove('bin'), os.remove('shir'), 1)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete('bin'), os.delete('shir'), 1)
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_rename_function_inside_rule_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove(os.remove('shir', 1), 2), 3)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.delete(os.delete('shir', 1), 2), 3)
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete($_)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_apply_rule_change_function_inside_rule_inside_rule(self):
    sourceCode = '''
      import os
      os.remove(os.remove(os.remove('shir', 1), 2), 3)
    '''

    expectedConvertedCode = '''
      import os
      os.delete(3, os.delete(2, os.delete(1, 'shir')))
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2)", 
         "patternToReplace": "os.delete($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RemoveFunctionTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Remove function tests")
    print("-------------------------------")

  def test_remove_function_without_params(self):
    sourceCode = '''
      import os as s
      s.remove()
      a = 1 + 2
    '''

    expectedConvertedCode = '''
      import os as s
      a = 1 + 2
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove()", 
         "patternToReplace": "" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_with_params(self):
    sourceCode = '''
      import os
      os.remove("shir")
      b = 1     
    '''

    expectedConvertedCode = '''
      import os
      b = 1
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class RemoveFunctionParamTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------")
    print("Remove function params tests")
    print("-------------------------------")

  def test_remove_function_last_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2)", 
         "patternToReplace": "os.delete($1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_first_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('binyamin')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2)", 
         "patternToReplace": "os.delete($2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_middle_param(self):
    sourceCode = '''
      import os
      os.remove('shir', 'binyamin', 'david')        
    '''

    expectedConvertedCode = '''
      import os
      os.delete('shir', 'david')        
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2, $3)", 
         "patternToReplace": "os.delete($1, $3)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_function_middle_param_of_objects(self):
    sourceCode = '''
      import os
      os.remove(os.path, object(), object())
    '''

    expectedConvertedCode = '''
      import os
      os.delete(os.path, object())
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($1, $2, $3)", 
         "patternToReplace": "os.delete($1, $3)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_all_function_params(self):
    sourceCode = '''
      import os
      os.remove(os.path, object(), object())
    '''

    expectedConvertedCode = '''
      import os
      os.delete()
    '''

    rule = { "module": "os", 
         "patternToSearch": "os.remove($_)", 
         "patternToReplace": "os.delete()" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ReplaceFuncParamsTests(UpdatorTests):
  def setUpClass():
    print("-----------------------------")
    print("Replace function params tests")
    print("-----------------------------")

  def test_replace_params_positions_when_params_are_int_variables(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x, y)     
    '''

    expectedConvertedCode = '''
      import math
      x = 2
      y = 3
      math.pow(y, x)
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($1, $2)", 
             "patternToReplace": "math.pow($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_params_are_compound_vars(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(x + f(1,2) / g(y), z)     
    '''

    expectedConvertedCode = '''
      import math
      x = 2
      y = 3
      math.pow(z, x + f(1,2) / g(y))
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($1, $2)", 
             "patternToReplace": "math.pow($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_params_hard_coded_int(self):
    sourceCode = '''
      import math
      math.pow(2, 3)     
    '''

    expectedConvertedCode = '''
      import math
      math.pow(3, 2)
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($1, $2)", 
             "patternToReplace": "math.pow($2, $1)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_params_hard_coded_strings(self):
    sourceCode = '''
      import stringTool as stool
      stool.join('shir', 'binyamin')     
    '''

    expectedConvertedCode = '''
      import stringTool as stool
      stool.join('binyamin', 'shir')  
    '''

    rule = { "module": "stringTool", 
             "property": "stringTool.join",
             "patternToSearch": "stringTool.join($1, $2)", 
             "patternToReplace": "stringTool.join($2, $1)",
             "assignmentRule": "auto" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("stringTool", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_pattern_inside_pattern(self):
    sourceCode = '''
      import math
      x = 2
      y = 3
      math.pow(math.pow(4, 5), y)
    '''

    expectedConvertedCode = '''
      import math
      x = 2
      y = 3
      math.pow(y, math.pow(5, 4))
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($1, $2)", 
             "patternToReplace": "math.pow($2, $1)" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_when_function_was_assigned(self):
    sourceCode = '''
      import math
      a = math.pow
      a(1, 2)
    '''

    expectedConvertedCode = '''
      import math
      a = math.pow
      a(2, 1)
    '''

    rule = { 
      "module": "math",
      "property": "math.pow",
      "patternToSearch": "math.pow($1, $2)",
      "patternToReplace": "math.pow($2, $1)",
      "assignmentRule": "auto" 
    }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_for_all_function_instances(self):
    sourceCode = '''
      import math
      a = math.pow
      a(1, 2)
      math.pow(3,4)
    '''

    expectedConvertedCode = '''
      import math
      a = math.pow
      a(2, 1)
      math.pow(4,3)
    '''

    rule = { 
      "module": "math",
      "property": "math.pow",
      "patternToSearch": "math.pow($1, $2)",
      "patternToReplace": "math.pow($2, $1)",
      "assignmentRule": "auto"
    }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_update_all_function_instances_when_params_are_variables(self):
    sourceCode = '''
      import math
      a = math.pow
      x = 1
      y = 2
      t = 3
      z = 4
      m.a = 1
      a(x, y)
      math.pow(t, z)
    '''

    expectedConvertedCode = '''
      import math
      a = math.pow
      x = 1
      y = 2
      t = 3
      z = 4
      m.a = 1
      a(y, x)
      math.pow(z, t)
    '''

    rule = { 
      "module": "math",
      "property": "math.pow",
      "patternToSearch": "math.pow($1, $2)",
      "patternToReplace": "math.pow($2, $1)",
      "assignmentRule": "auto" 
    }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_params_positions_for_all_function_alias_instances(self):
    sourceCode = '''
      import math as m
      a = m.pow
      a(1, 2)
      m.pow(3,4)
    '''

    expectedConvertedCode = '''
      import math as m
      a = m.pow
      a(2, 1)
      m.pow(4,3)
    '''

    rule = { 
      "module": "math",
      "property": "math.pow",
      "patternToSearch": "math.pow($1, $2)",
      "patternToReplace": "math.pow($2, $1)",
      "assignmentRule": "auto" 
    }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_position_param_value(self):
    sourceCode = '''
      import sklearn as skl
      skl.pipeline.FeatureUnion(None)
    '''

    expectedConvertedCode = '''
      import sklearn as skl
      skl.pipeline.FeatureUnion('drop')
    '''

    rule = { "module": "sklearn",
             "patternToSearch": "sklearn.pipeline.FeatureUnion(None)",
             "patternToReplace": "sklearn.pipeline.FeatureUnion('drop')" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("sklearn", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_keyword_param_value(self):
    sourceCode = '''
      import sklearn as skl
      skl.preprocessing.quantile_transform(copy=False)
    '''

    expectedConvertedCode = '''
      import sklearn as skl
      skl.preprocessing.quantile_transform(copy=True)
    '''

    rule = { "module": "sklearn",
             "patternToSearch": "sklearn.preprocessing.quantile_transform(copy=False)", 
             "patternToReplace": "sklearn.preprocessing.quantile_transform(copy=True)" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("sklearn", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ReplaceParamsTypesTests(UpdatorTests):
  def setUpClass():
    print("------------------------------------")
    print("Replace function params types tests")
    print("------------------------------------")

  def test_replace_position_params_to_keyword_params(self):
    sourceCode = '''
      import math
      math.pow(3, 4)
    '''

    expectedConvertedCode = '''
      import math
      math.pow(num1=3, num2=4)
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow($1, $2)", 
             "patternToReplace": "math.pow(num1=$1, num2=$2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_keyword_params_to_position_params(self):
    sourceCode = '''
      import math
      math.pow(num1=3, num2=4)
    '''

    expectedConvertedCode = '''
      import math
      math.pow(3, 4)
    '''

    rule = { "module": "math", 
             "patternToSearch": "math.pow(num1=$1, num2=$2)", 
             "patternToReplace": "math.pow($1, $2)" }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_replace_position_param_to_keyword_params_compounded(self):
    sourceCode = '''
      import pandas as pd
      df = pd.DataFrame([[1]])
      df.rename({0: 1}, {0: 2})
    '''

    expectedConvertedCode = '''
      import pandas as pd
      df = pd.DataFrame([[1]])
      df.rename(index={(0): 1}, columns={(0): 2})
    '''

    rule = { 
            "module": "pandas", 
            "assignmentPattern": "$1 = pandas.DataFrame($_)",
            "patternToSearch": "$1.rename($2, $3)", 
            "patternToReplace": "$1.rename(index=$2, columns=$3)",
            "assignmentRule": "manual" 
            }
             
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)
    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ChangeAttributeTests(UpdatorTests):
  def setUpClass():
    print("----------------------")
    print("Change attribute tests")
    print("----------------------")

  def test_rename_attr(self):
    sourceCode = '''
      import os
      os.path
    '''

    expectedConvertedCode = '''
      import os
      os.full_path
    '''

    rule = { "module": "os", "patternToSearch": "os.path", "patternToReplace": "os.full_path" }
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_attr_with_continuity(self):
    sourceCode = '''
      import os
      os.name.upper()
    '''

    expectedConvertedCode = '''
      import os
      os.full_name.upper()
    '''

    rule = { "module": "os", 
            "patternToSearch": "os.name", 
            "patternToReplace": "os.full_name" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_attr_inside_attr(self):
    sourceCode = '''
      import os
      os.name.upper
    '''

    expectedConvertedCode = '''
      import os
      os.name.up
    '''

    rule = { "module": "os", 
            "patternToSearch": "os.name.upper",
            "patternToReplace": "os.name.up" }
            
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_rename_attr_inside_attr_as_assignment(self):
    sourceCode = '''
      import os
      a = os.name
      a.upper
    '''

    expectedConvertedCode = '''
      import os
      a = os.name
      a.up
    '''

    rule = { "module": "os", 
            "patternToSearch": "os.name.upper",
            "patternToReplace": "os.name.up",
            "property": "os.name",
            "assignmentRule": "auto"
          }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_remove_attr(self):
    sourceCode = '''
      import os
      os.path
    '''

    expectedConvertedCode = '''
      import os
    '''

    rule = { "module": "os", "patternToSearch": "os.path", "patternToReplace": "" }
    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("os", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_attr_value(self):
    sourceCode = '''
      import pandas
      pandas.config.build = True
    '''

    expectedConvertedCode = '''
      import pandas
      pandas.config.build = 'auto'
    '''

    rule = { "module": "pandas",
            "patternToSearch": "pandas.config.build = True",
            "patternToReplace": "pandas.config.build = 'auto'" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class CombinationTypeTests(UpdatorTests):
  def setUpClass():
    print("-------------------------------------")
    print("Change in Combination of Types tests")
    print("-------------------------------------")

  def test_change_attr_use_to_function_use(self):
    sourceCode = '''
      import pandas as pd
      pd.name = 'myName'
    '''

    expectedConvertedCode = '''
      import pandas as pd
      pd.setName('myName')
    '''

    rule = { "module": "pandas",
            "patternToSearch": "pandas.name = $1",
            "patternToReplace": "pandas.setName($1)" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_compound_attr_use_to_function_use_as_assignment(self):
    sourceCode = '''
      import pandas
      m = pandas.MultiIndex.from_tuples([(1, 'ab'), (2, 'bb'), (3, 'cb')])
      m.name = 'myName'
    '''

    expectedConvertedCode = '''
      import pandas
      m = pandas.MultiIndex.from_tuples([(1, 'ab'), (2, 'bb'), (3, 'cb')])
      m = m.setName('myName')
    '''

    rule = { "module": "pandas",
            "assignmentPattern": "$1 = pandas.MultiIndex.from_tuples($_)",
            "patternToSearch": "$1.name = $2", 
            "patternToReplace": "$1 = $1.setName($2)",
            "assignmentRule": "manual" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_compound_attr_use_to_function_use_with_alias(self):
    sourceCode = '''
      import pandas as pd
      m = pd.MultiIndex.from_tuples([(1, 'ab'), (2, 'bb'), (3, 'cb')])
      m.name = 'myName'
    '''

    expectedConvertedCode = '''
      import pandas as pd
      m = pd.MultiIndex.from_tuples([(1, 'ab'), (2, 'bb'), (3, 'cb')])
      m = m.setName('myName')
    '''

    rule = { "module": "pandas", 
            "assignmentPattern": "$1 = pandas.MultiIndex.from_tuples($_)",
            "patternToSearch": "$1.name = $2", 
            "patternToReplace": "$1 = $1.setName($2)",
            "assignmentRule": "manual" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_funtion_use_to_attr_use(self):
    sourceCode = '''
      import pandas
      pandas.setName('myName')
    '''

    expectedConvertedCode = '''
      import pandas
      pandas.name = 'myName'
    '''

    rule = { "module": "pandas",
            "patternToSearch": "pandas.setName($1)",
            "patternToReplace": "pandas.name = $1" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_compound_funtion_use_to_attr_use(self):
    sourceCode = '''
      import pandas
      pandas.MultiIndex.setName('myName')
    '''

    expectedConvertedCode = '''
      import pandas
      pandas.MultiIndex.name = 'myName'
    '''

    rule = { "module": "pandas",
            "patternToSearch": "pandas.MultiIndex.setName($1)",
            "patternToReplace": "pandas.MultiIndex.name = $1" }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("pandas", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

class ChangeFuncReturnTests(UpdatorTests):
  def setUpClass():
    print("---------------------------------------")
    print("Change in function return values tests")
    print("---------------------------------------")

  def test_change_func_return_list_order(self):
    sourceCode = '''
      import math as m
      [x, y] = m.getPosition()
    '''

    expectedConvertedCode = '''
      import math as m
      [y, x] = m.getPosition()
    '''

    rule = { 
              "module": "math",
              "patternToSearch": "[$1, $2] = math.getPosition()", 
              "patternToReplace": "[$2, $1] = math.getPosition()"
            }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("math", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)

  def test_change_func_return_from_value_to_list_of_vars(self):
    sourceCode = '''
      import http
      handler = http.server.SimpleHTTPRequestHandler
      serverStatus = http.server.getStatus(handler)
    '''

    expectedConvertedCode = '''
      import http
      handler = http.server.SimpleHTTPRequestHandler
      [serverStatus, code] = http.server.getStatus(handler)
    '''

    rule =  { 
              "module": "http",
              "patternToSearch": "$1 = http.server.getStatus($_)", 
              "patternToReplace": "[$1, code] = http.server.getStatus($_)"
            }

    self.insertRule(rule)
    self.createCodeFile(sourceCode)
    self.updatorRun("http", fileToConvert)

    actualConvertedCode = self.dropWhitespace(self.readCodeFile())
    expectedConvertedCode = self.dropWhitespace(expectedConvertedCode)
    self.assertTrue(actualConvertedCode == expectedConvertedCode)


