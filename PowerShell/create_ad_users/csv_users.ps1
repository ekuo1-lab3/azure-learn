# Import the Active Directory module
Import-Module ActiveDirectory

# Import the CSV file
$csvPath = "C:\Users\Public\Documents\users2.csv"
$userList = Import-Csv -Path $csvPath

# Initialize hashtable for other attributes
$otherAttributes = @{}

# Remove common properties from headers (Name, Password, Enabled)
$headers = $userList[0].PSObject.Properties.Name
$commonProperties = @('Name', 'accountpassword', 'enabled')
$headers = $headers | Where-Object { $_ -notin $commonProperties }

# Specify the OU path
$ouPath = "OU=aad-connect-ou,DC=yp,DC=toll"

# Loop through each row in the CSV file and create the user

foreach ($user in $userList) {
    
    Write-Host $user
    # Extract user properties from CSV
    $name = $user.Name
    $password = $user.accountpassword
    $enabled = [System.Convert]::ToBoolean($user.Enabled)  # Convert string to boolean
    
    # Clear previous attributes
    $otherAttributes.Clear()
    $removeAttributes = @()

    # Populate specific attributes from CSV dynamically
    foreach ($header in $headers) {
        if ("" -eq $user.$header) {
            # Remove these attributes if not populated in csv
            $removeAttributes += $header
        }
        else {
            $otherAttributes[$header] = $user.$header
        }
    }

    if (Get-ADUser -Filter { SamAccountName -eq $name }) {
        # User exists, update attributes
        if ($removeAttributes) {
            Set-ADUser -Identity $name `
                -Enabled $enabled `
                -Replace $otherAttributes `
                -Clear $removeAttributes
        }
        else {
            Set-ADUser -Identity $name `
                -Enabled $enabled `
                -Replace $otherAttributes `
        
        }
        Write-Host "Updated user: $name" -ForegroundColor Yellow
    }
    else {
        # Create the new AD user
        New-ADUser `
            -Name $name `
            -AccountPassword (ConvertTo-SecureString $password -AsPlainText -Force) `
            -Enabled $enabled `
            -OtherAttributes $otherAttributes `
            -Path $ouPath 
        Write-Host "Created user: $name" -ForegroundColor Yellow
    }
}

Write-Host "AD User creation from CSV completed." 
