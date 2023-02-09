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


def cli(cmd_args, print_output=False, fmt_json=True):
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


usage_message = 'confluent schema-purge [-h] [--subject-prefix SUBJECT_PREFIX] [--api-key API_KEY] [--api-secret API_SECRET] [--context CONTEXT] [--env ENV] [--secrets-file SECRETS_FILE]'

parser = argparse.ArgumentParser(description='Deletes schemas'
                                             'This plugin assumes confluent CLI v3.0.0 or greater',
                                 usage=usage_message)

parser.add_argument('--subject-prefix', help='List schemas for subjects matching the prefix')
parser.add_argument('--api-key', help='The API key')
parser.add_argument('--api-secret', help='The API secret')
parser.add_argument('--context', help='The CLI context name')
parser.add_argument('--env', help='The environment id')
parser.add_argument('--secrets-file', help='Path to a JSON file with the API key and secret, '
                                           'the --api-key and --api-secret flags take priority')

args = parser.parse_args()

list_schema_cmd = ['confluent', 'schema-registry', 'schema', 'list', '--output', 'json']
delete_schema_cmd = ['confluent', 'schema-registry', 'schema', 'delete', '--force', '--permanent', '--version', 'all']
if args.api_key is None and args.api_secret is None and args.secrets_file is None:
    print("You must specify --api-key and --api-secret or --secrets-file")
    exit(1)

if args.context is not None:
    list_schema_cmd.append('--context')
    list_schema_cmd.append(args.context)
    delete_schema_cmd.append('--context')
    delete_schema_cmd.append(args.context)
if args.env is not None:
    list_schema_cmd.append('--environment')
    list_schema_cmd.append(args.env)
    delete_schema_cmd.append('--environment')
    delete_schema_cmd.append(args.env)
if args.subject_prefix is not None:
    list_schema_cmd.append('--subject-prefix')
    list_schema_cmd.append(args.sa)
if args.api_key is None and args.api_secret is None:
    with open(args.secrets_file) as json_file:
        creds_json = json.load(json_file)
        api_key = creds_json['api_key']
        api_secret = creds_json['api_secret']
else:
    api_key = args.api_key
    api_secret = args.api_secret

list_schema_cmd.append('--api-key')
list_schema_cmd.append(api_key)
list_schema_cmd.append('--api-secret')
list_schema_cmd.append(api_secret)

delete_schema_cmd.append('--api-key')
delete_schema_cmd.append(api_key)
delete_schema_cmd.append('--api-secret')
delete_schema_cmd.append(api_secret)
delete_schema_cmd.append('--subject')

schema_list_json = cli(list_schema_cmd)

schema_ids = []
for json_schema in schema_list_json:
    print("Found schema %s at version %s" % (json_schema['subject'], json_schema['version']))
    schema_ids.append(json_schema['subject'])

do_delete = input("Are you sure you want to delete all schemas? y|n  ")
if do_delete != 'y':
    print('Quitting and leaving all schemas in-place')
    exit(0)
else:
    for schema_id in schema_ids:
        delete_schema_cmd.append(schema_id)
        print(cli(delete_schema_cmd, fmt_json=False))
        delete_schema_cmd.pop()
