#!/usr/bin/env python

import urllib2
import json
import requests


service_id = '6XvgWOfUdWNBihdCwX5x9a'
api_key = "e2a1af9cacbbd8622222c04a7b34de36"
api_base = "https://api.fastly.com"
acl_name = "fastly_acl_block"
active_version = ''
acl_id = ''

#find active version 
url = api_base + "/service/" + service_id + "/version"
headers = {'content-type': 'application/json', 'Fastly-Key':api_key}
r = requests.get(url, headers=headers)

response = r.json()

for version in response:
    if version['active']:
        active_version = str(version['number'])

print active_version

#find ACL ID
url = api_base + "/service/" + service_id + "/version/" + active_version + "/acl/" + acl_name
r = requests.get(url, headers=headers)
response = r.json()
acl_id = str(response['id'])

print acl_id


#add entry

print acl_name
url = api_base + "/service/" + service_id + "/acl/" + acl_id + "/entry"
headers = {'content-type': 'application/json', 'Fastly-Key':api_key, 'accept':'application/json'}
payload = '{"ip": "5.5.5.5", "subnet": 32, "negated": false}'
r = requests.post(url, data=payload, headers=headers)
response = r.status_code
print response







