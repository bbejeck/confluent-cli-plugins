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
import subprocess
import json
import requests
import shutil


def cli(cmd_args, print_output, fmt_json=True):
    results = subprocess.run(cmd_args, capture_output=True)
    if results.returncode != 0:
        print(str(results.stderr, 'UTF-8'))
        exit(results.returncode)
    if fmt_json:
        final_result = json.loads(results.stdout)
    else:
        final_result = str(results.stdout, 'UTF-8')

    if print_output:
        print("Debug: %s" % final_result)

    return final_result


parser = argparse.ArgumentParser(description='Lists the Confluent CLI Plugins available')

parser.add_argument('--token', required=True, help='Your personal access token to use GitHub API')
parser.add_argument('--path', required=True, help='Path to save file to disk')

args = parser.parse_args()

url = 'https://api.github.com/repos/bbejeck/confluent-cli-plugins/contents/'
headers = {'Authorization': 'Bearer %s' % args.token,
           'Accept': 'application/vnd.github+json',
           'X-GitHub-Api-Version': '2022-11-28'}

api_response = requests.get(url, headers=headers)

plugins = {}
plugin_indx = 1
result_json = api_response.json()
for repo_entry in result_json:
    entry_type = repo_entry['type']
    if entry_type == 'dir':
        plugins[plugin_indx] = repo_entry['name']
        plugin_indx += 1
        
print("Available plugins to install:")
for key in plugins:
    print("%s: %s" % (key, plugins[key]))

plugins_to_download = input("Enter a single number or a comma separated list to install plugin(s): ")

for plugin_index in plugins_to_download.split(','):
    plugin_url = url + plugins[int(plugin_index)]
    plugin_file = requests.get(plugin_url, headers)
    if plugin_file.status_code == 200:
        full_json = plugin_file.json()[0]
        file_name = full_json['name']
        print("Getting plugin %s" % file_name)
        file_download = full_json['download_url']
        file_response = requests.get(file_download, headers, stream=True)

        with open(args.path + '/' + file_name, 'wb') as out_file:
            shutil.copyfileobj(file_response.raw, out_file)
        print("Successfully wrote %s to %s" % (file_name, args.path))
