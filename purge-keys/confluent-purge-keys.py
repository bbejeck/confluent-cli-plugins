#!/usr/bin/env python3


import argparse
import subprocess
import json


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


parser = argparse.ArgumentParser(description='Purges API keys for the current user '
                                             'This plugin assumes confluent CLI v3.0.0 or greater')

parser.add_argument('--resource', help='The resource id to filter results by')
parser.add_argument('--env', help='The environment id to purge keys from')
parser.add_argument('--sa', help='The service account id to purge keys from')

args = parser.parse_args()

cmd = ['confluent', 'api-key', 'list', '-o', 'json']

if args.env is not None and args.sa is not None:
    print("You can only specify one of environment id or service-account")
    exit(1)

if args.resource is not None:
    cmd.append('--resource')
    cmd.append(args.resource)
if args.env is not None:
    cmd.append('--environment')
    cmd.append(args.env)
if args.sa is not None:
    cmd.append('--service-account')
    cmd.append(args.sa)
if args.env is None and args.sa is None:
    cmd.append('--current-user')

api_keys_json = cli(cmd, False)
num_api_keys = len(api_keys_json)
if num_api_keys > 0:
    do_purge = input("Found %s API keys are you sure you want to purge them (y/n): " % num_api_keys)
    if do_purge == 'y':
        for api_key_obj in api_keys_json:
            del_cmd = ['confluent', 'api-key', 'delete', api_key_obj['key'], '--force']
            result = cli(del_cmd, False, fmt_json=False)
            print(result)
    else:
        print("Not purging keys, so quitting now")
else:
    print("No API keys found")



