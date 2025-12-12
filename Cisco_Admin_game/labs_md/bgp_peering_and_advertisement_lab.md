# BGP Peering and Advertisement Lab

Establish an eBGP session and advertise a specific prefix; verify neighbor and advertised routes.


## Diagram

```mermaid
graph LR
  n1[📡 Router]
  n2[🔀 Main Switch]
  n3[🖥️ Workstation]
  n1 --> n2
  n2 --> n3
```


## Steps

### Step : Configure BGP neighbor

**Expected:**
- `router bgp 65000`
- ` neighbor 203.0.113.2 remote-as 65001`
### Step : Advertise network

**Expected:**
- `network 10.100.0.0 mask 255.255.255.0`
### Step : Verify BGP

**Expected:**
- `show ip bgp summary`
- `show ip bgp 10.100.0.0`

## Simulated Outputs

- `show ip bgp summary` => `Neighbor 203.0.113.2 State/PfxRcd 4/1`
- `show ip bgp 10.100.0.0` => `*> 10.100.0.0/24 0.0.0.0`