#!/usr/bin/env python

import urllib2
import json
import sys
import requests
import re
import splunk.Intersplunk as si
import splunk.entity as entity
import splunk.mining.dcutils as dcu

logger = dcu.getLogger()

class FastlyACL(object):
    """ Adds an entry to the fastly_acl_block on the provided service ID,
    expects CIDR notations.

    ##Syntax
        fastly_acl fieldname=<field> serviceid=<service ID>

    ##Description
    Adds an entry to the fastly_acl_block service, if the ACL does not exists
    it will return an error. Expects data in CIDR notation, see 

    ##Example

    """
    def __init__(self, APIKey):
        """
        Fastly Contructor
            Provides the necessary pieces to make a rest calls via the Fastly API
            @param APIKey: api key to use in a query
        """
        self._apiKey = APIKey
        self._apiBase = "https://api.fastly.com"
        self._aclName = "fastly_acl_block"
        self._activeVersion = ''
        self._aclID = ''
        self._serviceID = ''


    def _getAclID(self):
        """
        Gets the ACL ID that is named after the aclName variable
        """
        url = self._apiBase + "/service/" + self._serviceID + "/version/" + self._activeVersion + "/acl/" + self._aclName
        headers = {'content-type': 'application/json', 'Fastly-Key':self._apiKey}
        r = requests.get(url, headers=headers)
        response = r.json()
        self._aclID = str(response['id'])
        return self._aclID

    def setServiceID(self, serviceID):
        """
        Sets the Service ID to use in the calls
        @param serviceID
        """
        self._serviceID = serviceID

    def _getActiveVersion(self):
        """
        Find active service version
        """
        url = self._apiBase + "/service/" + self._serviceID + "/version"
        headers = {'content-type': 'application/json', 'Fastly-Key':self._apiKey}
        r = requests.get(url, headers=headers)

        response = r.json()

        for version in response:
            if version == 'msg':
                if re.match("Record not found",response['msg']):
                    logger.exception("could not find latest version for serviceID: ",self._serviceID)
                    print "Error - could not find the latest version for serviceID: ", self._serviceID
                    sys.exit(1)
            else:
                if version['active']:
                    self._activeVersion = str(version['number'])
                    return self._activeVersion
    
    def addACL(self,ip):
        """
        Add an ACL entry to fastly_acl_block
        @param ip address to add
        returns call response code
        """

        #if we do not have an active version lets grab one
        if self._activeVersion == '':
            self._getActiveVersion()

        #same case with ACL ID
        if self._aclID == '':
            self._getAclID()

        url = self._apiBase + "/service/" + self._serviceID + "/acl/" + self._aclID + "/entry"
        headers = {'content-type': 'application/json','Fastly-Key':self._apiKey, 'accept':'application/json'}
        payload = '{"ip": "' + ip + '", "subnet": 32, "negated": false}'
        r = requests.post(url, data=payload, headers=headers)
        response = r.status_code
        return response

def getKey(sessionKey):
    # list api_key
    ent = entity.getEntities('fastly/conf/setupentity',namespace='fastly', owner='nobody',sessionKey=sessionKey)

    # return first set of cred
    for value in ent.values():
        return value['api_key']

if __name__ == '__main__':

    results, dummyresults, settings = si.getOrganizedResults()
    keywords, options = si.getKeywordsAndOptions()
    
    try:
        # get session key from settings
        s_key = settings['sessionKey']

        # retrive APIKey for Faroo from the setup entity
        APIKey = getKey(s_key)

        # faroo object
        FastlyACL = FastlyACL(APIKey)

        # set the serviceID we will be working in
        if options['serviceid']:
            FastlyACL.setServiceID(options['serviceid'])
        else:
            logger.exception("serviceID not provided")

        answers = []
        field_to_match = options['fieldname']
        if len(results) > 999:
            logger.exception("could not find latest version for serviceID: ",self._serviceID)
            print "Error - trying to add more than 1000 entries to a single ACL, this will not work, only 1000 entries allowed per ACL"
            sys.exit(1)

        for entry in results:
            if entry[field_to_match]:
                response = FastlyACL.addACL(entry[field_to_match])
                answers.append({"response":response,"entry":entry[field_to_match]})
#                print "Fastly Response,entry\n{0},{1}".format(response,entry[field_to_match])
        
        #output answers
        si.outputResults(answers)
            

    except Exception as e:
        results = si.generateErrorResults(str(e))
        logger.exception(e)
        si.outputResults(results)
