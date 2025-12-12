# ACL and Access Restriction Lab

Goal: Implement ACLs on a router to allow only DNS and HTTP from a user subnet to a server, deny everything else, and verify with pings and connection tests.


## Diagram

```mermaid
graph LR
  n2([📡 Router])
  n2 --> n3([🗄️ Server Subnet\n(10.2.2.10)])
```

## Visual Diagram

<svg xmlns="http://www.w3.org/2000/svg" width="600" height="280" viewBox="0 0 600 280">
<style> .node { fill:#f8f9fa; stroke:#333; stroke-width:1.5 } .nlabel { font-family:Segoe UI, Arial, sans-serif; font-size:12px; }</style>
<line x1="120" y1="80" x2="240" y2="80" stroke="#222" stroke-width="2" />
<line x1="280" y1="80" x2="400" y2="80" stroke="#222" stroke-width="2" />
<rect class="node" x="60" y="60" rx="6" ry="6" width="120" height="36" />
<text class="nlabel" x="68" y="80">User Subnet</text>
<rect class="node" x="220" y="60" rx="6" ry="6" width="120" height="36" />
<text class="nlabel" x="228" y="80">📡 Router</text>
<rect class="node" x="380" y="60" rx="6" ry="6" width="120" height="36" />
<text class="nlabel" x="388" y="80">🗄️ Server Subnet\n(10.2.2.10)</text>
</svg>

## Steps

### Step : Create ACL to permit DNS and HTTP
Create standard/extended ACL permitting tcp 80 and udp/tcp 53 from user subnet to server and deny others.

**Expected:**
- `ip access-list extended USER_TO_SRV\n permit tcp 10.1.1.0 0.0.0.255 host 10.2.2.10 eq 80\n permit udp 10.1.1.0 0.0.0.255 host 10.2.2.10 eq 53\n permit tcp 10.1.1.0 0.0.0.255 host 10.2.2.10 eq 53\n deny ip any any`
### Step : Apply ACL to interface
Apply the ACL in the correct direction on the router interface facing users.

**Expected:**
- `interface gigabitEthernet0/1\n ip access-group USER_TO_SRV in`
### Step : Verify access
From a user host attempt: ping server, curl http://10.2.2.10, and dig @10.2.2.10 www.example.com

**Expected:**
- `ping 10.2.2.10`
- `curl http://10.2.2.10`
- `nslookup www.example.com 10.2.2.10`

## Simulated Outputs

- `curl http://10.2.2.10` => `http:200 OK`
- `nslookup www.example.com 10.2.2.10` => `answer:10.2.2.10`