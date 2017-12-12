### Fastly + Splunk  
provides Fastly Pre-Built Commands and Reports for Splunk

## Description
* Adds the `fastlyacl` search command to Splunk. This adds ACLs to a Edge dictionary called [fastly\_acl\_block] to the selected service. To read more on Edge dictionary please visit <https://docs.fastly.com/guides/edge-dictionaries/about-edge-dictionaries>. Note that an ACL can only hold 1000 entries at a time keep in mind of this when using this command. 

more to come 

## Installation
* Grab a Fastly API Key from your Fastly admin
* `git clone https://github.com/fastly/soc/tree/master/fastly_splunk_app
$SPLUNK_HOME/etc/apps/fastly` 
* `cd $SPLUNK_HOME/etc/apps/fastly` and run `sudo ./setup.sh <FastLY API Key> <service ID>` for each serviceID to prepare for accepting ACL
* Configure Fastly Splunk App and Fastly API Key
* Start blocking


