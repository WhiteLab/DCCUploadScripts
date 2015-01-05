# source code obtained from https://github.com/ENCODE-DCC/WranglerScripts
from pic2str import pic2str
import sys
import re
from ENCODETools import GetENCODE
from ENCODETools import LoginGSheet
from ENCODETools import FindGSpreadSheet
from ENCODETools import FindGWorkSheet
from ENCODETools import FindGSheetCells
from ENCODETools import WriteJSON
import os
import mimetypes
from identity import keys

def get_data_uri(infile):
	try:
	     path = os.getcwd()+"/"+infile
	     with open(path,"rb") as f:
		data = f.read()
		temp_uri = data.encode("base64").replace("\n", "")
		mime_type = mimetypes.guess_type(path)
		data_uri = {'href':temp_uri, 'type': str(mime_type[0])}#'data:' + str(mime_type[0]) + ';base64,' + temp_uri
		return data_uri
	except :
		print sys.exc_info()[0] #>> sys.stderr, 'Cannot open input file'

if __name__ == "__main__":
    '''
This script will read in a google spreadsheet of objects and save them to json
'''

    json_file = 'import.json'

    email = "flyDCCuploads@gmail.com" # Stanford accounts won't work!
    password = "DCCuploads"

    spreadname = 'Fly_biosample_Characterization'  #sys.argv[1]
    typelist = ['biosample_characterization'] #[sys.argv[2]]

    sheetclient = LoginGSheet(email,password)

    # get the spreadsheet id
    [spreadid,spreadsheet] = FindGSpreadSheet(sheetclient,spreadname)

    print 'Processing spread sheet: ' + spreadname
    # check for data of each potential object type
    object_list = []
    for workname in typelist:
        print 'Processing work sheet: ' + workname
        # find the worksheet
        [workid,worksheet] = FindGWorkSheet(sheetclient,spreadid,workname)
        
        if workid:
            # get rows
            rows = sheetclient.GetListFeed(spreadid, workid).entry
	    print 'number of rows: ' + str(len(rows))
	    # get list of compressed header names
            headers = rows[0].custom.keys()
            print 'headers'
	    print headers
            # get cells from sheet
            cells = FindGSheetCells(sheetclient,spreadid,workid)
            # get schema for current object type
            object_schema = GetENCODE(('/profiles/' + workname + '.json'),keys)
            
            # for each header name, replace the compressed name with the full name
            for colindex,header in enumerate(headers):
                headers[colindex] = cells[colindex].content.text

            # for each row, load in each key/value pair that has a value assigned
            # convert value to schema defined type

            for row in rows:
                new_object = {u'@type':[workname,u'item']}
                for header in headers:
                    if object_schema[u'properties'].has_key(header):
                        value = row.custom[header.replace('_','').lower()].text
			print value
                        if value is not None:
                            # need to fix dates before adding them. Google API does not allow disabling of autoformat.
                            # use regexp to check for dates (MM/DD/YYYY)
                            # then format them as we enter them (YYYY-MM-DD)
                            if re.search(r'\d{1,2}/\d{1,2}/\d{1,4}' , value):
                                date = value.split('/')
                                value = date[2] + '-' + date[0] + '-' + date[1]
                            #print header + "::" + value

 
                            if object_schema[u'properties'][header][u'type'] == 'string':
                                new_object.update({header:unicode(value)})
                            elif object_schema[u'properties'][header][u'type'] == 'integer':
                                new_object.update({header:int(value)})
                            elif object_schema[u'properties'][header][u'type'] == 'float':
                                new_object.update({header:float(value)})
                            elif object_schema[u'properties'][header][u'type'] == 'array':
                                value = value.split(', ')
                                if object_schema[u'properties'][header][u'items'][u'type'] == 'string':
                                    new_object.update({header:value})
                                elif object_schema[u'properties'][header][u'items'][u'type'] == 'object':
                                    sub_object = dict()
                                    for prop_value_pair in value:
                                        pair = prop_value_pair.split(': ')
                                        sub_object[pair[0]] = pair[1]
                                    new_object.update({header: [sub_object]})
                            # upload image as attachment object
                            elif object_schema[u'properties'][header][u'type'] == 'object':
                                if header == 'attachment':
				    sub_object = {}
			            print 'filename' + str(value)
                                    sub_object[u'href'] = get_data_uri(value)#image data
				#remove @type for new_object
				#print new_object
				#if new_object.has_key(u'@type'):
				#	del new_object[u'@type']
				#print new_object
				new_object.update({header: sub_object})
    #                            print new_object
#                                print object_schema[u'properties'][header][u'properties'][u'type']
#                                if object_schema[u'properties'][header][u'properties'][u'type'] == 'string':  
#                                    print object_schema[u'properties'][header][u'properties'][u'title'] + '\n'
#                                    sub_object = dict()
#                                    for prop_value_pair in value:
#                                        pair = prop_value_pair.split(': ')
#                                        sub_object[pair[0]] = pair[1]
#                                    new_object.update({header: [sub_object]})


    # elif object_schema[u'properties'][header][u'items'][u'type'] is 'integer':
    # new_object.update({header:int(value)})
                    
                object_list.append(new_object)

    print 'Writing '+ str(len(object_list))+ ' objects to JSON file: '+ json_file
    # write object to file
    WriteJSON(object_list,json_file)
    print('Done.')

