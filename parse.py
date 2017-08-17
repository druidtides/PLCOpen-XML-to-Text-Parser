#!/usr/bin/env python
"""Convert PLCOpen XML file to readble text
Available functions:
- parse_file: 
"""

__author__ = 'jamie.ross@nightsail.ie (Jamie Ross P.Eng.)'

from __future__ import print_function
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import codecs
import unicodedata
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()
inputfilename = args.filename
datasource = open(inputfilename)

		
tree = ET.parse(datasource)
root = tree.getroot()
projectname = root[1].get("name")
version = root[1].get("version")
modificationDateTime = root[1].get("modificationDateTime")

fileoutname = inputfilename + '_output.txt'
f1 = codecs.open(fileoutname, 'w+', encoding='utf-8')
print('Processing ',inputfilename)
print('Output file name = ',fileoutname)
print( "====================================================================================================================",file=f1)
print( "Source Project: ", projectname," Version: ",version,' ModificationDateTime: ',modificationDateTime, file=f1)
print( "====================================================================================================================",file=f1)
print( 'DATA TYPE DEFINITION',file=f1 )
print( "--------------------------------------------------------------------------",file=f1)
root = tree.getroot()
for datatype in root.findall("./types/dataTypes/*"):
	name = datatype.get('name')
	for datastructure in datatype.findall("./baseType/*"):
		struct = datastructure.tag
		if struct == 'array':
			lower = datastructure[0].get("lower")
			upper = datastructure[0].get("upper")
			type = datastructure[1][0].tag
			if type == 'derived':
				parenttype = datastructure[1][0].get('name')
				type = '['+parenttype+']'
			print(name+': Array '+lower+'...'+upper+' of '+type,file=f1)
		elif struct == 'struct':
			print(name+'= Struct:',file=f1)
			for element in datastructure.findall("./variable"):
				el_name = element.get("name")
				type = element[0][0].tag
				if type == 'derived':
					parenttype = element[0][0].get('name')
					type = '['+parenttype+']'
				print('\t'+el_name+': '+type,file=f1)
			
for pou in tree.findall("./types/pous/*"):
	name = pou.get('name')
	poutype = pou.get('pouType')
	print('POU: ',name)
	print( "====================================================================================================================",file=f1)
	print( "POU: ", name," pouType: ",poutype, file=f1)
	print( "--------------------------------------------------------------------------",file=f1)
	print( "INTERFACE\n",file=f1)
	for varType in ['inputVars','outputVars','inOutVars','externalVars','localVars']:
		varTypeText = {'inputVars':'Input Variables','outputVars':'Output Variables','inOutVars': 'Input Ouput Variables','externalVars':'External Variables','localVars':'Local Variables'}
		print(varTypeText[varType])
		print( "\t%s:" % varTypeText[varType],file=f1)
		for temp in pou.findall("./interface/%s/*" % varType):
			name = temp.get('name')
			comment = temp.get('comment')
			for types in temp.findall("./type/*"):
				type = types.tag 
				if type == 'derived':
					typesrc = types.get('name')
					print( "\t\t",name," [",typesrc,"] : ",comment,file=f1)
				else:
					typesrc = ''
					print( "\t\t",name," ",type," : ",comment,file=f1)

	print( "--------------------------------------------------------------------------",file=f1)
	print( "BODY\n",file=f1)
	for temp in pou.findall("./body/ST/*"):
		str =ET.tostring(temp,encoding="us-ascii",method="html")
		soup = BeautifulSoup(str,'html.parser')
		text = soup.get_text('\n')
		print(unicodedata.normalize('NFKD', text).encode('ascii','ignore'),file=f1)
f1.close()

		
		
