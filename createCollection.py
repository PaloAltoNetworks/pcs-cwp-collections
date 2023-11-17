import requests
import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(
    prog='python3 createCollection.py',
    description='This sets up the subnet and security group in Prisma Cloud for Agentless scanning',
    epilog='For further documentation go to: https://github.com/PaloAltoNetworks/pcs-cwp-agentless'
)

COMPUTE_API_ENDPOINT = os.getenv("COMPUTE_API_ENDPOINT", "https://us-east1.cloud.twistlock.com/us-1-23456789")
PRISMA_USERNAME = os.getenv("PRISMA_USERNAME", "")
PRISMA_PASSWORD = os.getenv("PRISMA_PASSWORD", "")
SKIP_VERIFY = bool(int(os.getenv("SKIP_VERIFY", "0")))

def getToken(username, password, api_endpoint, verify):
    headers = {
        "Content-Type": "application/json"
    }
    body = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{api_endpoint}/api/v1/authenticate", json=body, headers=headers, verify=verify)
    if response.status_code == 200:
        return response.json()["token"]
    
    print(response.json())
    sys.exit(2)

def create_collection(
        api_endpoint,
        token,
        name, 
        images=["*"], 
        hosts=["*"], 
        labels=["*"], 
        containers=["*"], 
        functions=["*"],
        namespaces=["*"],
        app_ids=["*"],
        account_ids=["*"],
        code_repos=["*"],
        clusters=["*"],
        color="#000000",
        verify=True,
        override=False
    ):
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    data = {
        "name": name,
        "images": images,
        "hosts": hosts,
        "labels": labels,
        "containers": containers,
        "functions": functions,
        "namespaces": namespaces,
        "appIDs": app_ids,
        "accountIDs": account_ids,
        "codeRepos": code_repos,
        "clusters": clusters, 
        "color": color
    }

    print(f"Trying to create collection {name}...")
    response = requests.post(f"{api_endpoint}/api/v1/collections", json=data, headers=headers, verify=verify)

    if response.status_code == 200:
        print(f"Collection {name} successfully created.")
    
    else:
        print(f"Error while creating collection {name}. Error: {response.json()['err']}")
        if override:
            print(f"Trying to update collection {name}...")
            response = requests.put(f"{api_endpoint}/api/v1/collections/{name}", json=data, headers=headers, verify=verify)
            
            if response.status_code == 200:
                print(f"Collection {name} successfully updated.")
            
            else:
                print(f" Error while updating collection {name}.")
                print(response.text)
                sys.exit(2)
        
        else:
            sys.exit(2)


if __name__ == "__main__":
    parser.add_argument("-n", "--collection-name", type=str, required=True, help="Name of the collection")
    parser.add_argument("-u", "--username", type=str, default=PRISMA_USERNAME, help="Prisma Cloud Access Key Id or username")
    parser.add_argument("-p", "--password", type=str, default=PRISMA_PASSWORD, help="Prisma Cloud Secret Key or password")
    parser.add_argument("-e", "--compute-api-endpoint", type=str, default=COMPUTE_API_ENDPOINT, help="Prisma Cloud Compute Api Endpoint")
    parser.add_argument("-i", "--images", nargs='+', default=["*"], help="Images for the collection. If empty will catch all.")
    parser.add_argument("-H", "--hosts", nargs='+', default=["*"], help="Hosts for the collection. If empty will catch all.")
    parser.add_argument("-l", "--labels", nargs='+', default=["*"], help="Labels for the collection. If empty will catch all.")
    parser.add_argument("-c", "--containers", nargs='+', default=["*"], help="Containers for the collection. If empty will catch all.")
    parser.add_argument("-f", "--functions", nargs='+', default=["*"], help="Functions for the collection. If empty will catch all.")
    parser.add_argument("-N", "--namespaces", nargs='+', default=["*"], help="Namespaces for the collection. If empty will catch all.")
    parser.add_argument("-a", "--app-ids", nargs='+', default=["*"], help="appIDs for the collection. If empty will catch all.")
    parser.add_argument("-A", "--account-ids", nargs='+', default=["*"], help="accountIDs for the collection. If empty will catch all.")
    parser.add_argument("-r", "--code-repos", nargs='+', default=["*"], help="codeRepos for the collection. If empty will catch all.")
    parser.add_argument("-C", "--clusters", nargs='+', default=["*"], help="Clusters for the collection. If empty will catch all.")
    parser.add_argument("-o", "--color", type=str, default="#000000", help="color of the collection.")
    parser.add_argument("--skip-tls-verify", action="store_false", default=SKIP_VERIFY, help="Skip TLS verification")
    parser.add_argument("-O", "--override", action="store_true", help="Override any existing collection.")


    args = parser.parse_args()
    username = args.username
    password = args.password
    compute_api_endpoint = args.compute_api_endpoint
    verify = not args.skip_tls_verify

    create_collection(
        compute_api_endpoint,
        getToken(username, password, compute_api_endpoint, verify),
        name=args.collection_name,
        images=args.images,
        hosts=args.hosts,
        labels=args.labels,
        containers=args.containers,
        functions=args.functions,
        namespaces=args.namespaces,
        app_ids=args.app_ids,
        account_ids=args.account_ids,
        code_repos=args.code_repos,
        clusters=args.clusters,
        color=args.color,
        verify=verify,
        override=args.override
    )
