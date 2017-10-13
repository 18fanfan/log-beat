from ConfigParser import ConfigParser
import os

value_parser = { 'log_list': 'json_parser', 
		'severity': 'uppercase' }

section_as_list = ['Company']


script_base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = "%s/%s" % (script_base_dir, 'config.ini')

class ConfigLoader(object):
	
	def __init__(self, config_path):
		c = ConfigParser()
		c.read(config_path)

		def parser(item):
			option, value = item[0], item[1]
			if option in value_parser:
				p_func = value_parser[option]
				return (option, getattr(self, p_func)(value))

			return item
	
		for section in c.sections():
			if section in section_as_list:
				key = section
				value = {}
				value.update(c.items(section))
				entry = tuple([key, value])
				self.__dict__.update([entry])
			else:
			    after_convert = map(parser, c.items(section))
			    self.__dict__.update(after_convert)
	

	def json_parser(self, v):
		from json import loads
		return loads(v)

	def uppercase(self, v):
		return v.upper()


config = ConfigLoader(config_path)

if __name__ == '__main__':
	# test and verification
	c = ConfigParser()
	c.read(config_path)
	
	attr_list = []
	for section in c.sections():
		if section in section_as_list:
			attr_list.append('Company')
		else:
			attr_list += c.options(section)

	print "all attribute in config: %s" % str(attr_list)
	print "option, value, type"

	for attr in attr_list:
		print "%s: |%s|, %s" % (attr, getattr(config, attr), type(getattr(config, attr)))

