#Connect-AzAccount -UseDeviceAuthentication -Tenant 38eac198-359f-4b75-ab72-fc189f23cace

Write-host "wowow"

$rg = "ps_rg"
$location = "Australia East"

New-AzResourceGroup -Name $rg -Location $location

$sshRule = New-AzNetworkSecurityRuleConfig -Name ssh-rule -Description "Allow SSH" `
    -Access Allow -Protocol Tcp -Direction Inbound -Priority 100 `
    -SourceAddressPrefix Internet -SourcePortRange * `
    -DestinationAddressPrefix * -DestinationPortRange 22 

$nsg = New-AzNetworkSecurityGroup -ResourceGroupName $rg `
    -Location $location -Name "sg" -SecurityRules $sshRule
      
$pip = New-AzPublicIpAddress -Name "pip" -ResourceGroupName $rg `
    -Location $location -Sku "Standard" -IdleTimeoutInMinutes 4 -AllocationMethod "static"

$pip_id = Get-AzPublicIpAddress -Name "pip" -ResourceGroupName $rg
Write-Host "Public IP address is $($pip_id.IpAddress)"

$subnet1 = New-AzVirtualNetworkSubnetConfig -Name "subnet1" -AddressPrefix "10.0.0.0/24" 
New-AzVirtualNetwork -AddressPrefix "10.0.0.0/16" -Location $location -Name "vnet1" `
    -ResourceGroupName $rg -Subnet $subnet1

$vnet = Get-AzVirtualNetwork -ResourceGroupName $rg -Name "vnet1"

$subnet1 = Get-AzVirtualNetworkSubnetConfig -Name "subnet1" -VirtualNetwork $vnet 
$IPconfig = New-AzNetworkInterfaceIpConfig -Name "IPConfig1" -Subnet $subnet1 -PublicIpAddress $pip
$nic = New-AzNetworkInterface -Name "nic1" -ResourceGroupName $rg -Location $location `
    -IpConfiguration $IPconfig -NetworkSecurityGroup $nsg

$username = "adminuser"
$password = ConvertTo-SecureString "123456789Mow" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($username, $password)

$VM = New-AzVMConfig -VMName 'vm' -VMSize "Standard_B1ls" -SecurityType "Standard"
$VM = Set-AzVMSourceImage -VM $VM -PublisherName "Canonical" -Offer "0001-com-ubuntu-server-focal" -Skus "20_04-lts" -Version "latest"
$VM = Add-AzVMNetworkInterface -VM $VM -NetworkInterface $nic
$VM = Set-AzVMOperatingSystem -VM $VM -Linux -Credential $cred -ComputerName "hello"

New-AzVM -ResourceGroupName $rg -Location $location -Vm $VM -Verbose