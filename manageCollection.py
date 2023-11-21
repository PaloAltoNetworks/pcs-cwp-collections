import requests
import argparse
import os
import sys
import json

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

parser = argparse.ArgumentParser(
    prog='python3 manageCollection.py',
    description='Useful for createting, updating and deleting Collections in Prisma Cloud Compute',
    epilog='For further documentation go to: https://github.com/PaloAltoNetworks/pcs-cwp-collections'
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

def upload_file(
        api_endpoint,
        token, 
        filename,
        verify=True,
        overwrite=False
    ):

    with open(filename) as f:
        data = json.loads(f.read())

    if not "name" in data:
        print(f"{filename} requires name parameter.")
        return False

    name = data["name"]
    return create_collection(
        api_endpoint,
        token,
        name,
        data, 
        verify,
        overwrite
    )

def create_collection(
        api_endpoint,
        token,
        name, 
        data,
        verify=True,
        overwrite=False
    ):
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }


    print(f"Trying to create collection {name}...")
    response = requests.post(f"{api_endpoint}/api/v1/collections", json=data, headers=headers, verify=verify)

    if response.status_code == 200:
        print(f"Collection {name} successfully created.")
        return True
    
    else:
        print(f"Error while creating collection {name}. Error: {response.json()['err']}")
        if overwrite:
            print(f"Trying to update collection {name}...")
            response = requests.put(f"{api_endpoint}/api/v1/collections/{name}", json=data, headers=headers, verify=verify)
            
            if response.status_code == 200:
                print(f"Collection {name} successfully updated.")
                return True
            
            else:
                print(f" Error while updating collection {name}.")
                print(response.text)
                return False
        
        else:
            return False

def delete_collection(
        api_endpoint,
        token,
        name,
        verify=True
    ):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.delete(f"{api_endpoint}/api/v1/collections/{name}", headers=headers, verify=verify)
    if response.status_code == 200:
        print(f"Collection {name} successfully deleted.")
        return True
    
    print(f"Collection {name} failed to be deleted. Error: {response.json()['err']}")
    return False


if __name__ == "__main__":
    parser.add_argument("-n", "--collection-name", type=str, help="Name of the collection")
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
    parser.add_argument("-O", "--overwrite", action="store_true", help="Overwrites any existing collection.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete an existing collection.")
    parser.add_argument("-D", "--delete-list", nargs='+', default=[], help="List of collections to be deleted.")
    parser.add_argument("-F", "--file", type=str, default="", help="Upload a collection from file in json format.")
    parser.add_argument("-P", "--path", type=str, default="", help="Bulk upload collections from directory.")

    args = parser.parse_args()
    username = args.username
    password = args.password
    compute_api_endpoint = args.compute_api_endpoint
    name = args.collection_name
    verify = not args.skip_tls_verify
    overwrite = args.overwrite
    delete = args.delete
    delete_list = args.delete_list
    filename = args.file
    path = args.path

    if delete and overwrite:
        parser.error("--delete and --overwrite cannot be used at the same time.")

    if delete and delete_list:
        parser.error("--delete and --delete_list cannot be used at the same time.")
    
    if filename and path:
        parser.error("--file and --path cannot be used at the same time.")

    if not (filename or path or name or delete_list):
        parser.error("--collection-name is required value.")

    if delete or delete_list:
        if delete:
            succeded = delete_collection(
                compute_api_endpoint,
                getToken(username, password, compute_api_endpoint, verify),
                name=name,
                verify=verify
            )

            if not succeded:
                sys.exit(2)

        if delete_list:
            deleted_colls = []
            not_deleted_colls = []
            for collection in delete_list:
                succeded = delete_collection(
                    compute_api_endpoint,
                    getToken(username, password, compute_api_endpoint, verify),
                    name=collection,
                    verify=verify
                )

                if succeded:
                    deleted_colls.append(collection)
                
                else:
                    not_deleted_colls.append(collection)

            if deleted_colls:
                print(f"Collections deleted: {', '.join(deleted_colls)}")
            else:
                print(f"Collections not deleted: None")

            if not_deleted_colls:
                print(f"Collections not deleted: {', '.join(not_deleted_colls)}")
            else:
                print(f"Collections not deleted: None")
                
    else:
        if filename:
            succeded = upload_file(
                compute_api_endpoint,
                getToken(username, password, compute_api_endpoint, verify),
                filename=filename,
                verify=verify,
                overwrite=overwrite
            )

            if succeded:
                print(f"{filename} successfully uploaded")

        elif path:
            succeded_files = []
            failed_files = []
            for filename in os.listdir(path):
                succeded = upload_file(
                    compute_api_endpoint,
                    getToken(username, password, compute_api_endpoint, verify),
                    filename=f"{path}/{filename}",
                    verify=verify,
                    overwrite=overwrite
                )

                if succeded:
                    succeded_files.append(filename)
                else:
                    failed_files.append(filename)

            if succeded_files:
                print(f"Succeded files: {', '.join(succeded_files)}")
            else:
                print(f"Succeded files: None")

            if failed_files:
                print(f"Failed files: {', '.join(failed_files)}")
            else:
                print(f"Failed files: None")

        else:
            data = {
                "name": name,
                "images": args.images,
                "hosts": args.hosts,
                "labels": args.labels,
                "containers": args.containers,
                "functions": args.functions,
                "namespaces": args.namespaces,
                "appIDs": args.app_ids,
                "accountIDs": args.account_ids,
                "codeRepos": args.code_repos,
                "clusters": args.clusters, 
                "color": args.color
            }

            succeded = create_collection(
                compute_api_endpoint,
                getToken(username, password, compute_api_endpoint, verify),
                name=name,
                data=data,
                verify=verify,
                overwrite=overwrite
            )

            if not succeded:
                sys.exit(2)