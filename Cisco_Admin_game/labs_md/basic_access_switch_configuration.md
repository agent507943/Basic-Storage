# Basic Access Switch Configuration

Configure VLANs, an SVI and assign access ports for a basic access switch.


## Steps

### Step : Create VLANs
Create VLAN 10 (DATA) and VLAN 20 (VOICE) on the switch.

**Expected:**
- `vlan 10\nname DATA`
- `vlan 20\nname VOICE`
### Step : Create SVI
Create SVI interface vlan 10 and assign IP 10.0.10.2/24.

**Expected:**
- `interface vlan 10\n ip address 10.0.10.2 255.255.255.0`
### Step : Assign Access Port
Configure interface GigabitEthernet0/1 as access for VLAN 10.

**Expected:**
- `interface gigabitEthernet0/1\n switchport mode access\n switchport access vlan 10`