#!/bin/env python3

# tqdm: https://pypi.org/project/tqdm/
# bs: https://beautiful-soup-4.readthedocs.io/en/latest/#searching-the-tree
# requests: https://docs.python-requests.org/en/master/user/quickstart/#cookies

import requests, os, sys
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
from PyInquirer import prompt
import urllib3
urllib3.disable_warnings()

moodle_url = ""
# login_url = ""
email, password = "", ""
course_url = ""

DOWN_FOLDER = "saved"

browser_cookie_string = os.environ.get("MOODLE_SESSION_COOKIE", None)

q1 = {"type": "input", "name": "murl", "message": "Enter moodle platform URL"}
q2 = {"type": "input", "name": "course", "message": "Enter course URL"}
q3 = {"type": "input", "name": "email", "message": "Email"}
q4 = {"type": "password", "name": "pass", "message": "Password"}

questions = []


if not moodle_url:
  questions.append(q1)
if not email:
  questions.append(q3)
if not password:
  questions.append(q4)

answers = prompt(questions)

if not moodle_url:
  moodle_url = answers['murl']
if not email:
  email = answers['email']
if not password:
  password = answers['pass']

s = requests.Session()
res = s.get(moodle_url, verify=False, allow_redirects=True)
soup = BS(res.text, features="lxml")
loginToken = soup.find(attrs={'name': 'logintoken'})['value']
post_url = soup.find(id="login")['action']

data = {
  'anchor': '',
  'logintoken': loginToken,
  'username': email,
  'password': password,
  'rememberusername': 1
}


p_res = s.post(post_url, data=data, verify=False,allow_redirects=True)
    

## loop for courses urls 
print("logged in successfuly")

def write_to_f(el):
    with open("f.txt", "w") as f:
        f.write(el.prettify())


def pprint(el):
    print(el.prettify())


if not os.access(DOWN_FOLDER, os.R_OK):
  os.system(f"mkdir '{DOWN_FOLDER}'")


while True:
  q = {'type': 'input', 'name':'course', 'message': 'Enter course url'}
  course_url = prompt(q)['course']

  res = s.get(course_url, verify=False)

  soup = BS(res.text, features="lxml")


  res = soup.find("ul", class_="topics")
  items = res.find_all("li")

  resource_links = list(filter(lambda x: "resource" in x.get("href"), res.find_all("a")))

  for link in tqdm(resource_links):

      resource_name = link.text
      resource_source = link.get("href")
      resource_extension = link.contents[0].get("src").split("/")[-1].split("-")[0]
      if "power" in resource_extension:
          resource_extension = "pptx"

      print(f"\n\nDownloading {resource_name}: {resource_extension.upper()}")
      # resp = requests.get(resource_source, cookies=formated_cookies)
      resp = s.get(resource_source)
      with open(f"{os.path.join(DOWN_FOLDER, resource_name)}.{resource_extension}", "wb") as f:
          f.write(resp.content)

  print("Downloads done")
