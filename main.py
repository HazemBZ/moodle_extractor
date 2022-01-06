#!/bin/env python3

# tqdm: https://pypi.org/project/tqdm/
# bs: https://beautiful-soup-4.readthedocs.io/en/latest/#searching-the-tree
# requests: https://docs.python-requests.org/en/master/user/quickstart/#cookies

import requests, os, sys
from bs4 import BeautifulSoup as BS
from tqdm import tqdm


url = ""

browser_cookie_string = os.environ.get("MOODLE_SESSION_COOKIE", None)


if sys.argv[1]:
    url = sys.argv[1]
else:
    print("no url specified")
    sys.exit()


if len(sys.argv) == 3:
    browser_cookie_string = sys.argv[2]

if not browser_cookie_string:
    print('no moodle cookie on "MOODLE_SESSION_COOKIE" Env variable')
    sys.exit(0)

formated_cookies = dict(map(lambda s: s.split("="), browser_cookie_string.split("; ")))
print(f"formatted cookie {formated_cookies}")

res = requests.get(url, cookies=formated_cookies)

soup = BS(res.text)


# li.activity resource modtype_resource -> ... -> div.activityinstance
# li#
# topics list : >>> res1 = soup.find('ul', class_="topics")
# topics items: >>> items = res1.find_all('li')

res1 = soup.find("ul", class_="topics")
items = res1.find_all("li")


def write_to_f(el):
    with open("f.txt", "w") as f:
        f.write(el.prettify())


def pprint(el):
    print(el.prettify())


resource_links = list(filter(lambda x: "resource" in x.get("href"), res1.find_all("a")))

for link in tqdm(resource_links):

    resource_name = link.text
    resource_source = link.get("href")
    resource_extension = link.contents[0].get("src").split("/")[-1].split("-")[0]
    if "power" in resource_extension:
        resource_extension = "pptx"

    print(f"\n\nDownloading {resource_name}: {resource_extension.upper()}")
    resp = requests.get(resource_source, cookies=formated_cookies)
    with open(f"{resource_name}.{resource_extension}", "wb") as f:
        f.write(resp.content)

print("Downloads done")
