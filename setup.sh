#G!/bin/bash

EXPECTED_ARGS=2
E_BADARGS=65

if [ $# -lt 2 ]
  then
echo "Usage: `basename $0` <FastLY API Key> <service ID>"
echo "Example `basename $0` e2a2af9cdcbba8622111c12a7e34de56 6yIm5Ep3CNoBYaegPSJ5DO"
  exit $E_BADARGS
fi

if [ $# -gt $EXPECTED_ARGS ]
then
echo "Too many arguments"
        exit $E_BADARGS
fi

service_id="$2"
token="$1"
#get current version
echo "preparing service $service_id"
version=$(curl -s -H "Fastly-Key: $token" https://api.fastly.com/service/$service_id/version | jq '.[-1].number')

echo "cloning service"
#clone current version
curl -s -X PUT https://api.fastly.com/service/$service_id/version/$version/clone -H "Fastly-Key:$token" -H "Content-Type: application/json" -H "Content-Type: application/x-www-form-urlencoded" -w "Response: %{http_code}\n" -o /dev/null

# get lastest version
version=$(curl -s -H "Fastly-Key: $token" https://api.fastly.com/service/$service_id/version | jq '.[-1].number')
echo "new version $version"

# Add Edge ACLs
echo "creating ACL 'fastly_acl_block'"
curl -s -X POST -H "Fastly-Key:$token" https://api.fastly.com/service/$service_id/version/$version/acl -d '{ "name": "fastly_acl_block"}' -H "Content-Type: application/json" -H "Accept: application/json" -w "Response: %{http_code}\n" -o /dev/null


# Creating Block Condition
echo "creating vcl snippet 'fastly_acl_block'"
snippet='name=fastly_acl_block&type=recv&priority=1&dynamic=1&content=if (req.http.Fastly-Client-IP ~ fastly_acl_block) { error 403 "Forbidden";}'

snippet_id=$(curl -s -X POST -H "Fastly-Key:$token" https://api.fastly.com/service/$service_id/version/$version/snippet -d "$snippet" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: application/json" | jq '.id'| sed -e 's/^"//' -e 's/"$//') 

curl -s -X PUT -H "Fastly-Key:$token" https://api.fastly.com/service/$service_id/snippet/$snippet_id -d "$snippet " -w "Response: %{http_code}\n" -o /dev/null

#install python requirements
echo "installing python requirements"
pip -q install -r requirements.txt

echo "Please make sure you activate version $version for service $service_id"
echo "completed!"
