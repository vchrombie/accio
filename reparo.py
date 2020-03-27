#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CHAOSS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Venu Vardhan Reddy Tekula <venuvardhanreddytekula8@gmail.com>
#     Sanjana Nayar <sanjananayar2k1@gmail.com>
#


import requests
import json
import sys
import os
from string import Template

years = "2015-2020"
owner = "Bitergia"

REPO = input("repo name: ")
dirname = input("path to repo: ")


def getlistoffiles(dirname):
    listoffile = os.listdir(dirname)
    allfiles = list()
    for entry in listoffile:
        fullpath = os.path.join(dirname, entry)
        if os.path.isdir(fullpath):
            allfiles = allfiles+getlistoffiles(fullpath)
        else:
            allfiles.append(fullpath)
    return(allfiles)


def main():

    listoffiles = getlistoffiles(dirname)

    FILES = []

    for f in listoffiles:
        count = 0
        try:
            for line in open(f):
                if "Copyright (C)" and "Authors" in line:
                    count = count+1
            if(count > 0):
                FILES.append(f)
        except UnicodeDecodeError:
            pass
    for item in FILES:
        api_func(item, dirname)


def api_func(items2, dirname):
    PATH_TO_FILE2 = items2.replace(dirname, '')
    PATH_TO_FILE = PATH_TO_FILE2.strip('/')
    LINK = "https://api.github.com/repos/chaoss/"

    data = requests.get(LINK + REPO + "/commits?path=" + PATH_TO_FILE)

    data = json.loads(data.content)

    authors_data = {}

    try:
        for item in reversed(data):
            data = item['commit']['author']
            if data['name'] not in authors_data.keys():
                authors_data[data['name']] = data['email']
    except TypeError:
        pass

    authors = [key + " <" + value + ">" for key, value in authors_data.items()]
    authors.append('')

    # print(authors)

    template_file = open("gpl-v3.tmpl")

    src = Template(template_file.read())

    sub_dict = {
        'years': years,
        'owner': owner,
        'authors': '\n#     '.join(authors)
    }

    result = src.substitute(sub_dict)

    with open(items2, 'r') as f:
        contents = f.readlines()
        i = 0
        for item in contents:
            if item.startswith('#'):
                i += 1

    with open(items2, 'w') as f:
        f.writelines(contents[i:])

    with open(items2, 'r') as f:
        contents = f.readlines()
        contents.insert(0, result+"\n")

    with open(items2, 'w') as f:
        contents = "".join(contents)
        f.write(contents)


if __name__ == "__main__":
    sys.exit(main())
