import json
import os
from string import Template

from dotenv import load_dotenv

import modules
from datetime import datetime

load_dotenv()

attack_version = ""

# Read versions file for ATT&CK version
with open("data/versions.json", "r", encoding="utf8") as f:
    attack_version = json.load(f)["current"]["name"]

# ATT&CK version
if attack_version.startswith("v"):
    full_attack_version = attack_version
    attack_version = attack_version[1:]

# Domains for stix objects
STIX_LOCATION_ENTERPRISE = os.getenv(
    "STIX_LOCATION_ENTERPRISE",
    "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
)
STIX_LOCATION_MOBILE = os.getenv(
    "STIX_LOCATION_MOBILE", "https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json"
)
STIX_LOCATION_ICS = os.getenv(
    "STIX_LOCATION_ICS", "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json"
)
STIX_LOCATION_PRE = os.getenv(
    "STIX_LOCATION_PRE", "https://raw.githubusercontent.com/mitre/cti/master/pre-attack/pre-attack.json"
)
domains = [
    {"name": "enterprise-attack", "location": STIX_LOCATION_ENTERPRISE, "alias": "Enterprise", "deprecated": False},
    {"name": "mobile-attack", "location": STIX_LOCATION_MOBILE, "alias": "Mobile", "deprecated": False},
    {"name": "ics-attack", "location": STIX_LOCATION_ICS, "alias": "ICS", "deprecated": False},
    {"name": "pre-attack", "location": STIX_LOCATION_PRE, "alias": "PRE-ATT&CK", "deprecated": True},
]

# banner for the website
default_banner_message = "This is a custom instance of the MITRE ATT&CK Website. The official website can be found at <a href='https://attack.mitre.org'>attack.mitre.org</a>."
BANNER_ENABLED = os.getenv("BANNER_ENABLED", True)
BANNER_MESSAGE = os.getenv("BANNER_MESSAGE", default_banner_message)

# Args for modules to use if needed
args = []

# Staged for pelican settings
staged_pelican = {}


def send_to_pelican(key, value):
    """Method to stage key value pairs for pelican use"""
    staged_pelican[key] = value


def check_versions_module():
    """Return if versions module is loaded"""
    if [key["module_name"] for key in modules.run_ptr if key["module_name"] == "versions"]:
        return True
    return False


def check_resources_module():
    """Return if resources module is loaded"""
    if [key["module_name"] for key in modules.run_ptr if key["module_name"] == "resources"]:
        return True
    return False


# Source names for ATT&CK
source_names = ["mitre-attack", "mitre-mobile-attack", "mitre-ics-attack", "mitre-pre-attack"]

# Declare file location of web pages
web_directory = "output"

# Parent web directory name
# leave parent directory name to first level for link tests
parent_web_directory = "output"

# Declare as empty string
subdirectory = ""

# directory for data used in site builds
data_directory = "data"


def set_subdirectory(subdirectory_str):
    """Method to globally set the subdirectory"""

    global subdirectory
    global web_directory

    subdirectory = subdirectory_str

    # Verify if website directory exists
    if not os.path.isdir(web_directory):
        os.makedirs(web_directory)

    # Add subdirectory to web directory
    web_directory = os.path.join(web_directory, subdirectory)

def generate_updates_list():
    """Creates a list of markdown update files from the static pages resources directory."""
    static_pages_dir = os.path.join("modules", "resources", "static_pages")
    updates_dict = {}
    updates_name = []
    updates_path = []
    for static_page in os.listdir(static_pages_dir):
        with open(os.path.join(static_pages_dir, static_page), "r", encoding="utf8") as md:
            content = md.read()
            if static_page.startswith("updates-"):
                temp_string = static_page.replace('.md','')
                temp_string = temp_string.split('-')
                temp_string = temp_string[1].capitalize() + ' ' + temp_string[2]
                updates_name.append(temp_string)
                temp_string = static_page.replace('.md','')
                updates_path.append("/resources/updates/" + temp_string)
    updates_name.sort(key=lambda date: datetime.strptime(date, "%B %Y"), reverse=True)
    updates_path.sort(key=lambda date: datetime.strptime(date, "/resources/updates/updates-%B-%Y"), reverse=True)
    updates_dict["updates_name"] = updates_name
    updates_dict["updates_path"] = updates_path
    return(updates_dict)

# Navigation list for resources (this is the list before adding the updates)
with open("data/resources_navigation.json", "r", encoding="utf8") as i:
    res_nav = json.load(i)

# Add the updates as children to the Updates section
updates_dict_list = generate_updates_list()
updates_index = 0
for i in range(len(res_nav["children"])):
    if res_nav["children"][i]["name"] == "Updates":
        updates_index = i

temp_dict = {}
for i in range(len(updates_dict_list["updates_name"])):
    temp_dict["name"] = updates_dict_list["updates_name"][i]
    temp_dict["path"] = updates_dict_list["updates_path"][i]
    temp_dict["children"] = []
    res_nav["children"][updates_index]["children"].append(temp_dict.copy())
    temp_dict = {}

def generate_attackcon_list():
    """Creates a list of attackcon files."""
    attackcon_md = []
    attackcon_name = []
    attackcon_path = []
    attackcon_dict = {}
    with open(os.path.join(data_directory, "attackcon.json"), "r", encoding="utf8") as f:
        attackcon = json.load(f)
    attackcon = sorted(attackcon, key=lambda a: datetime.strptime(a["date"], "%B %Y"), reverse=True)
    for i in range(len(attackcon)):
        attackcon_name.append(attackcon[i]["title"])
        title = "Title: " + attackcon[i]["title"] + "\n"
        name = attackcon[i]["date"].lower().replace(' ','-')
        template = "Template: general/attackcon-overview\n"
        attackcon_path.append("/resources/attackcon/" + name)
        save_as = "save_as: resources/attackcon/" + name + "/index.html\n"
        data = "data: "
        content = title + template + save_as + data
        attackcon_md.append(content)
    attackcon_dict["attackcon_name"] = attackcon_name
    attackcon_dict["attackcon_path"] = attackcon_path
    attackcon_dict["attackcon_md"] = attackcon_md
    return attackcon_dict

# Add the updates as children to the AttackCon section
attackcon_dict_list = generate_attackcon_list()
attackcon_index = 0
temp_dict = {}
for i in range(len(res_nav["children"])):
    if res_nav["children"][i]["name"] == "ATT&CKcon":
        attackcon_index = i

for i in range(len(attackcon_dict_list["attackcon_name"])):
    temp_dict["name"] = attackcon_dict_list["attackcon_name"][i]
    temp_dict["path"] = attackcon_dict_list["attackcon_path"][i]
    temp_dict["children"] = []
    res_nav["children"][attackcon_index]["children"].append(temp_dict.copy())
    temp_dict = {}

# Create the complete resources navigation list
with open("data/resources_navigation_list.json", "w", encoding="utf8") as i:
    i.write(json.dumps(res_nav))

# Set the resource nav variable to the json data. This is then used in website build
with open("data/resources_navigation_list.json", "r", encoding="utf8") as i:
    resource_nav = json.load(i)

# Location of html templates
templates_directory = "attack-theme/templates/"

javascript_path = "attack-theme/static/scripts/"

# Static style pelican files directory
static_style_dir = os.path.join("attack-theme", "static", "style/")


# Link to instance of the ATT&CK Navigator; change for to a custom location
navigator_link = "https://mitre-attack.github.io/attack-navigator/"

# Content directory
content_dir = "content/"

# Pelican pages directory
pages_dir = "content/pages"

# Pelican docs directory
docs_dir = "content/docs/"

# Markdown path for redirects
redirects_markdown_path = "content/pages/redirects/"

# markdown path for resources
resources_markdown_path = "content/pages/resources/"

# Redirect md string template
redirect_md_index = Template(
    "Title: ${title}\n"
    "Template: general/redirect-index\n"
    "RedirectLink: ${to}\n"
    "save_as: ${from}/index.html"
)
redirect_md = Template(
    "Title: ${title}\n"
    "Template: general/redirect-index\n"
    "RedirectLink: ${to}\n"
    "save_as: ${from}"
)

# Custom_alphabet used to sort list of dictionaries by domain name
# depending on domain ordering
custom_alphabet = ""
rest_of_alphabet = ""

for domain in domains:
    if not domain["deprecated"]:
        # Remove whatever comes after the -
        if "-" in domain["name"]:
            short_domain = domain["name"].split("-")[0]
        else:
            short_domain = domain["name"]

        # Get first character of domain
        custom_alphabet += short_domain.lower()[:1]

        # Add rest of characters, doesn't matter if it is repeated
        rest_of_alphabet += short_domain.lower()[1:]

custom_alphabet += rest_of_alphabet

# Constants used for generated layers
# ----------------------------------------------------------------------------
# usage:
#     domain: "enterprise", "mobile", "ics"
#     path: the path to the object, e.g "software/S1001" or "groups/G2021"
layer_md = Template(
    "Title: ${domain} Techniques\n"
    "Template: general/json\n"
    "save_as: ${path}/${attack_id}-${domain}-layer.json\n"
    "json: "
)
layer_version = "4.4"
navigator_version = "4.8.1"

# Directory for test reports
test_report_directory = "reports"

# Workbench credentials to use if pulling STIX from ATT&CK Workbench version 1.2.0 or later
WORKBENCH_USER = os.getenv("WORKBENCH_USER")
WORKBENCH_API_KEY = os.getenv("WORKBENCH_API_KEY")

GOOGLE_ANALYTICS = os.getenv("GOOGLE_ANALYTICS")
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION")
