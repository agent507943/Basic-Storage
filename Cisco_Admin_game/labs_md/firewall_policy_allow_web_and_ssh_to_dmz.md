# Firewall Policy: Allow Web and SSH to DMZ

Create policies and NAT (if needed) to allow HTTP and SSH to a DMZ web and management host.


## Steps

### Step : Create inbound HTTP rule
Add a rule permitting TCP 80 from outside to DMZ web server 198.51.100.10

**Expected:**
- `access-list OUT2DMZ permit tcp any host 198.51.100.10 eq 80`
### Step : Create inbound SSH rule for mgmt subnet
Permit SSH from 10.1.1.0/24 to management host 198.51.100.11

**Expected:**
- `access-list OUT2MGMT permit tcp 10.1.1.0 255.255.255.0 host 198.51.100.11 eq 22`