import azure.functions as func
import logging
import requests
import time
import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

scope = "https://graph.microsoft.com/.default"
graphApiVersion = "beta"  # "v1.0"
uri = "https://graph.microsoft.com/{v}/{r}"

# Storage account
connection_string = os.getenv("AzureWebJobsStorage")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "user-info"
blob_name = "user_info.json"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    query = (
    "users?$select=givenName,surname,accountEnabled,employeeId,"
    "userPrincipalName,mail,onPremisesSamAccountName,companyName,department,"
    "country,employeeHireDate,employeeLeaveDateTime,employeeType,jobTitle,"
    "onPremisesExtensionAttributes,"
    "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute1,"
    "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute2,"
    "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute3,"
    "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute6,"
    "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute7"
    "&$expand=manager($select=id,displayName,employeeId,onPremisesExtensionAttributes)"
    )

    next_link = uri.format(v=graphApiVersion, r=query)
    all_users = []
    auth_headers = get_token()

    while next_link:
        response = requests.get(next_link, headers=auth_headers)
        
        if response.status_code == 429:  # Throttled
            retry_after = int(response.headers.get("Retry-After", 60))
            logging.warning(f"Throttled, retrying after {retry_after} seconds")
            time.sleep(retry_after)
            continue  # Retry the current request
        
        if response.status_code == 200: # Success
            result = response.json()
            users = result.get('value', [])
            all_users.extend(users) 
            
            next_link = result.get('@odata.nextLink')  # Get the next page URL

        else: # Failed
            logging.error(f"Request failed: {response.status_code}")
            break
            
    if all_users:
        # Write JSON file to storage account
        json_data = json.dumps(all_users, indent=4)

        try:
            # Create the container if it doesn't exist
            container_client = blob_service_client.get_container_client(container_name)
            try:
                container_client.create_container()
            except ResourceExistsError:
                pass

            # Upload the JSON data to a blob
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(json_data, overwrite=True)

            return func.HttpResponse("JSON file created and uploaded to Azure Blob Storage.", status_code=200)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return func.HttpResponse(f"An error occurred: {e}", status_code=500)

    else:
        return func.HttpResponse(
            "No user data found or request failed.",
            status_code=404
        )


"""
Gets an authentication token from the default Azure credential provider.

Returns:
    dict: Headers containing the Authorization token.
"""
def get_token():
    credential = DefaultAzureCredential()
    token = credential.get_token(scope)
    auth_headers = {
        "Authorization": f"Bearer {token[0]}",
    }
    return auth_headers