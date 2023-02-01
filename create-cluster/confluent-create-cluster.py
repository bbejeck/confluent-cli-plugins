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


parser = argparse.ArgumentParser(description='Creates a Kafka cluster with API keys, '
                                             'Schema Registry with API keys and a client '
                                             'config template.'
                                             'This plugin assumes confluent CLI v3.0.0 or greater')

parser.add_argument('--name', required=True, help='The name for your Confluent Kafka Cluster')
parser.add_argument('--env', help='The environment name')
parser.add_argument('--cloud', default='aws', choices=['aws', 'azure', 'gcp'],
                    help='Cloud Provider, Defaults to aws')
parser.add_argument('--region', default='us-west-2', help='Cloud region e.g us-west-2 (aws), '
                                                          'westus (azure), us-west1 (gcp)  Defaults to us-west-2')
parser.add_argument('--geo', choices=['apac', 'eu', 'us'], default='us',
                    help='Cloud geographical region Defaults to us')
parser.add_argument('--client', choices=['clojure', 'cpp', 'csharp', 'go', 'groovy', 'java', 'kotlin',
                                         'ktor', 'nodejs', 'python', 'restapi',
                                         'ruby', 'rust', 'scala', 'springboot'],
                    default='java', help='Properties file used by client (default java)')
parser.add_argument("--debug", choices=['y', 'n'], default='n',
                    help="Prints the results of every command, defaults to n")

args = parser.parse_args()

debug = False if args.debug == 'n' else True

print("Creating the Kafka cluster")
cluster_json = cli(["confluent", "kafka", "cluster", "create", args.name,
                    "-o", "json", "--cloud", args.cloud, "--region", args.region], debug)

print("Generating api keys for the cluster")
creds_json = cli(["confluent", "api-key", "create", "--resource", cluster_json['id'], "-o", "json"], debug)

print("Enabling Schema Registry")
sr_json = cli(["confluent", "schema-registry", "cluster", "enable", "--cloud",
               cluster_json['provider'], "--geo", args.geo, "-o", "json"], debug)

print("Generating API keys for Schema Registry")
sr_creds_json = cli(["confluent", "api-key", "create", "--resource", sr_json['id'], "-o", "json"], debug)

print("Generating client config")
client_config = cli(["confluent", "kafka", "client-config", "create", args.client,
                     "--cluster", cluster_json['id'],
                     "--api-key", creds_json['api_key'],
                     "--api-secret", creds_json['api_secret'],
                     "--schema-registry-api-key", sr_creds_json['api_key'],
                     "--schema-registry-api-secret", sr_creds_json['api_secret']],
                    debug, fmt_json=False)

print("\nStart %s client configs ##################################################################################\n" %
      args.client)
print(client_config)
print("End %s client configs ####################################################################################" %
      args.client)
