param location string = 'australia east'

targetScope = 'subscription'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'vm-rg2'
  location: location
}
