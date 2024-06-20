import requests
import time
import json
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
scope = "https://graph.microsoft.com/.default"
TOKEN = credential.get_token(scope)

def fetch_all_users():
    # query = "$filter=startswith(displayName,'test')&$select=displayName,employeetype&$expand=manager($select=displayName)&$top=5"
    # query = "$select=displayName,employeetype&$expand=manager($select=displayName)&$top=100"
    query = (
        "$select=givenName,surname,accountEnabled,employeeId,"
        "userPrincipalName,mail,onPremisesSamAccountName,companyName,department,"
        "country,employeeHireDate,employeeLeaveDateTime,employeeType,jobTitle,"
        "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute1,"
        "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute2,"
        "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute3,"
        "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute6,"
        "extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute7"
        "&$expand=manager($select=id,displayName,employeeId,extension_9873fae9bd9d427e99a57f2ffae59240_msDS_cloudExtensionAttribute2)"
    )
    url = f"https://graph.microsoft.com/beta/users?{query}"
    all_users = []
    
    while url:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {TOKEN[0]}"}
        )
        
        if response.status_code == 429:  # Throttled
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Throttled, retrying after {retry_after} seconds")
            time.sleep(retry_after)
            continue  # Retry the current request
        
        if response.status_code == 200: # Success
            result = response.json()
            users = result.get('value', [])
            all_users.extend(users) 
            
            url = result.get('@odata.nextLink')  # Get the next page URL
        else:
            print(f"Request failed: {response.status_code}")
            break

    # Write all users data to a JSON file 
    with open('users.json', 'w') as f:
        json.dump(all_users, f, indent=4)

start = time.time()
fetch_all_users()
end = time.time()
print("Elapsed time:", end - start)