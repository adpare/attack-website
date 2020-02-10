import json
import requests
import os
from modules import site_config

def get_stix_data():
    """Set up proxy if any and get STIX data"""

    # Set proxy
    proxy  = ""
    if site_config.args.proxy is not None:
        proxy = site_config.args.proxy
    proxyDict = { 
        "http"  : proxy,
        "https" : proxy
    }

    use_local_stix = True
    for domain in site_config.domains:
        if not (os.path.isfile('{0}/{1}.json'.format(site_config.stix_directory, domain))):
            use_local_stix = False

    if (not os.path.isdir(site_config.stix_directory)):
        os.mkdir(site_config.stix_directory)
    try:
        for domain in site_config.domains:
            r = requests.get(f"https://raw.githubusercontent.com/mitre/cti/master/{domain}/{domain}.json", 
            verify=False, proxies=proxyDict)
            
            with open(os.path.join(site_config.stix_directory, domain + "_old.json"), 'w+') as f:
                f.write(json.dumps(r.json()))
                
                if (site_config.args.refresh or not os.path.isdir(site_config.stix_directory) or not use_local_stix):
                    with open(os.path.join(site_config.stix_directory, domain + ".json"), 'w+') as f:
                        f.write(json.dumps(r.json()))

    except:
        print("Unable to reach stix repository. Are you behind a (--proxy)?")