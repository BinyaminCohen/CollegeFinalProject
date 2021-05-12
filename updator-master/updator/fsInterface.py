class FsInterface:

	def readFileSourceCode(self, filepath):
		with open(filepath, 'rb') as f:
			sourceCode = f.read()
			f.close()
			return sourceCode

	def saveConvertedCode(self, filepath, convertedCode):
		with open(filepath, 'w') as f:
			f.write(convertedCode)
			f.close()