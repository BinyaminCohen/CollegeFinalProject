import pymongo

class DbInterface:

	def __init__(self):
		client = pymongo.MongoClient('localhost', 27017)
		self.db = client.updator_db
		self.rules = self.db.rules
		self.createIndex()

	def dropRules(self):
		self.rules.drop()

	def createIndex(self):
		self.rules.create_index([("module", pymongo.ASCENDING), ("patternToSearch", pymongo.ASCENDING)], unique=True)

	def findLibs(self):
 		return self.rules.aggregate([{"$group": {"_id": "$module", "count": {"$sum": 1}}}])

	def insertRule(self, rule):
		rule["active"] = True
		self.rules.insert_one(rule)

	def insertRules(self, rules):
		for rule in rules:
			rule["active"] = True
		self.rules.insert_many(rules)

	def deactivateRule(self, rule):
		self.rules.update_one(rule, { "$set": {"active": False}})

	def reactivateRule(self, rule):
		self.rules.update_one(rule, { "$set": {"active": True}})

	def findRulesByLib(self, module):
		return self.rules.find({"module": module, "active": True})

	def findAllRulesByLib(self, module):
		return self.rules.find({"module": module})

