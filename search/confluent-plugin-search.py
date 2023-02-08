#!/usr/bin/env python3

#  Copyright (c) 2023 Confluent
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import requests
import os
import stat

parser = argparse.ArgumentParser(description='Lists the Confluent CLI Plugins available')

parser.add_argument('--token', required=True, help='Your personal access token to use GitHub API')
parser.add_argument('--path', default='/usr/local/bin', help='Path to save commands')

args = parser.parse_args()

url = 'https://api.github.com/repos/bbejeck/confluent-cli-plugins/contents/'
headers = {'Authorization': 'Bearer %s' % args.token,
           'Accept': 'application/vnd.github+json',
           'X-GitHub-Api-Version': '2022-11-28'}

api_response = requests.get(url, headers=headers)
if api_response.status_code != 200:
    print("There was an error connecting to GitHub - %s: %s" % (api_response.status_code, api_response.reason))
    exit(1)

plugins = {}
plugin_indx = 1
result_json = api_response.json()
for repo_entry in result_json:
    entry_type = repo_entry['type']
    if entry_type == 'dir' and repo_entry['name'] != 'search':
        plugins[plugin_indx] = repo_entry['name']
        plugin_indx += 1

print("Available plugins to install:")
for key in plugins:
    print("%s: %s" % (key, plugins[key]))

plugins_to_download = input("Enter a single number or a comma separated list to install plugin(s) or n to quit: ")
if plugins_to_download == 'n':
    print("Bye!!")
    exit(0)

for plugin_index in plugins_to_download.split(','):
    plugin_url = url + plugins[int(plugin_index)]
    plugin_file = requests.get(plugin_url, headers)
    if plugin_file.status_code == 200:
        full_json = plugin_file.json()[0]
        file_name = full_json['name']
        print("Getting plugin %s" % file_name)
        file_download = full_json['download_url']
        file_response = requests.get(file_download, headers, stream=True)
        cmd_file = args.path + '/' + file_name
        with open(cmd_file, 'w', encoding='utf-8') as out_file:
            out_file.writelines(file_response.text)
            st = os.stat(cmd_file)
            os.chmod(cmd_file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print("Successfully installed %s to %s" % (file_name, args.path))
