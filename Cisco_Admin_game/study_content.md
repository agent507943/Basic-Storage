# Cisco Admin Study Guide

This study guide is organized to support the interactive Cisco Admin Learning Game. It covers commands, configuration patterns, and design guidance for routers, switches, and related services.

## Basics & CLI Navigation

- Privileged EXEC: `enable` -> returns `#` prompt.
- Global configuration: `configure terminal` (or `conf t`).
- Saving config: `copy running-config startup-config` or `write memory`.
- Viewing configs: `show running-config`, `show startup-config`.

## Interface and L2 Switch Config

- Set access VLAN on an interface:

  interface GigabitEthernet0/1
  switchport mode access
  switchport access vlan 10

- Configure trunking (802.1Q):

  interface GigabitEthernet0/1
  switchport trunk encapsulation dot1q
  switchport mode trunk
  switchport trunk native 999   # optional

- Configure VLAN SVI on layer-3 switch:

  interface vlan 10
   ip address 10.0.10.1 255.255.255.0
   no shutdown

- Verify commands:
  - `show vlan brief`
  - `show interfaces status`
  - `show ip interface brief`

## Spanning Tree & Redundancy

- View STP: `show spanning-tree`.
- Change STP mode: (platform dependent) `spanning-tree mode rapid-pvst`.
- Root placement: set `spanning-tree vlan <vlan> root primary` or adjust priority.
- HSRP/VRRP for gateway redundancy:

  interface vlan 10
   ip address 10.0.10.2 255.255.255.0
  standby 10 ip 10.0.10.1
  standby 10 priority 110

## Aggregation: EtherChannel

- LACP active mode configuration:

  interface range Gi0/1 - Gi0/2
   channel-group 1 mode active

- Verify: `show etherchannel summary`, `show running-config interface port-channel 1`.

## Routing Protocols

- OSPF basic:

  router ospf 1
   network 10.0.0.0 0.0.255.255 area 0

  Verify: `show ip ospf neighbor`, `show ip ospf database`.

- EIGRP basic:

  router eigrp 100
   network 10.0.0.0
   no auto-summary

- BGP basics:

  router bgp 65000
   neighbor 203.0.113.2 remote-as 65001
   neighbor 203.0.113.2 description ISP-PRIMARY

  Verify: `show ip bgp summary`, `show ip bgp neighbors`.

## Redistribution & Route Policies

- Always tag routes when redistributing to avoid loops.
- Example Redistribute OSPF into BGP with route-map:

  ip prefix-list OSPF-IN permit 10.0.0.0/8
  route-map OSPF-INTO-BGP permit 10
   match ip address prefix-list OSPF-IN
   set metric 100
  router bgp 65000
   redistribute ospf 1 route-map OSPF-INTO-BGP

- Use `show ip route` to verify redistributed routes and tags.

## NAT & Security

- Basic dynamic NAT for inside networks:

  ip nat inside source list 10 interface Gig0/0 overload
  access-list 10 permit 10.0.0.0 0.0.255.255

- ACL placement: apply extended ACLs as close to the source as possible for filtering.
- Use named ACLs (`ip access-list extended NAME`) for clarity.

## QoS & Performance

- Use class-maps and policy-maps to shape and police traffic.
- Example: classify voice and give priority:

  class-map match-any VOICE
   match ip dscp ef
  policy-map QOS
   class VOICE
    priority percent 30

- Monitor with `show policy-map interface` and `show mls qos interface`.

## Monitoring & Management

- Syslog: `logging host <ip>` and `logging trap <level>`.
- NTP: `ntp server <ip>` for time sync.
- SNMP: configure read-only and secure community strings or SNMPv3.
- Backup configs to Git/TFTP/FTP and automate pulls for config management.

## Automation & Modern APIs

- Use SSH + scripts, or automation tools like Ansible (netconf/napalm modules) for repeatable changes.
- Cisco modern APIs: RESTCONF/NETCONF and model-driven telemetry on supported platforms.
- Store configs in Git and validate with linters before applying.

## Troubleshooting Tips and Commands

- Routing: `show ip route`, `show ip bgp summary`, `show ip ospf neighbor`.
- Interfaces: `show interfaces`, `show interfaces status`, `show ip interface brief`.
- VLANs: `show vlan brief`, `show mac address-table`.
- ACLs: `show access-lists`, `show ip interface` to see applied ACLs.
- NAT: `show ip nat translations`, `clear ip nat translation *` (use with caution).
- Use `debug` commands sparingly and on non-production or with scheduled windows.

## Design Guidelines

- Use hierarchical design: access, distribution, core.
- Plan addressing and summarization for scalable routing.
- Use VRFs for tenant separation and EVPN/MPLS for multi-tenant fabrics.
- Test changes in staging environment and use maintenance windows for risky changes.

## Firewalls and Perimeter Security

- Firewall types: stateful packet filters, NGFW (next-generation firewall), application-layer (proxy), IDS/IPS complementary systems.
- Common Cisco firewall products: Cisco ASA, Cisco Firepower/FTD, and cloud-native firewall services. Each has CLI and GUI/management options (ASDM, FMC, or cloud consoles).
- Basic firewall elements:
  - Zones / interfaces: group interfaces into security zones and apply policies between zones.
  - Access policies: define rules by source, destination, service/port, application, users.
  - NAT: translate inside/outside addresses when required (static, dynamic, PAT).
  - Stateful inspection: connection tracking to allow return traffic.

## Firewall Management & Best Practices

- Management: use a central manager where possible (Cisco FMC for Firepower, Panorama for Palo Alto) to push consistent policies and collect telemetry.
- Hardening: limit management plane access (ACLs to management interfaces), use SSH keys, enable AAA, and enable logging to a secure syslog or SIEM.
- Change workflow: maintain firewall rules in version control, review rule changes in staging, and apply during maintenance windows. Use rule descriptions and tagging for auditability.
- High availability: configure active/standby or active/active with state sync for session preservation during failover.
- Monitoring & troubleshooting:
  - Use `show` commands on the platform (e.g., `show access-list`, `show nat detail`, product-specific commands) and check logs for dropped traffic.
  - Test policies with crafted traffic (telnet/netcat from a controlled host) and capture packets when needed.

## DHCP (Server, Relay, and Best Practices)

- DHCP roles:
  - DHCP server: issues IP configuration (address, mask, gateway, DNS, options).
  - DHCP relay (ip helper-address): forwards DHCP broadcast requests from clients across routed networks to a centralized DHCP server.

- IOS example (basic pool):

  ip dhcp excluded-address 10.0.10.1 10.0.10.10
  ip dhcp pool DATA
   network 10.0.10.0 255.255.255.0
   default-router 10.0.10.1
   dns-server 10.0.0.5

- Important options often used in voice deployments:
  - Option 150 / 66: TFTP server(s) for IP phone provisioning.
  - Option 3: router (default gateway).

- DHCP troubleshooting commands:
  - `show ip dhcp binding` — list active leases
  - `show ip dhcp pool` — pool usage and statistics
  - `debug ip dhcp server` / `debug ip dhcp client` — use carefully in lab/maintenance windows

## DNS: Records, Configuration, and Troubleshooting

- Common DNS record types:
  - A / AAAA: host address records (IPv4 / IPv6).
  - CNAME: canonical name (alias) records.
  - PTR: reverse DNS (pointer) records.
  - SRV: service records (used by some services like SIP).

- Examples:
  - BIND zone snippet for an A record:

    example.com. IN SOA ns1.example.com. admin.example.com. (
      2025121001 ; serial
      3600       ; refresh
      900        ; retry
      604800     ; expire
      86400 )    ; minimum
    @ IN NS ns1.example.com.
    ns1 IN A 10.0.0.5
    www IN A 10.0.10.20

- IOS local DNS (DNS server entries and simple host records):

  ip name-server 10.0.0.5
  ip host printer1 10.0.10.50

- DNS troubleshooting:
  - `nslookup` / `dig` from a client or management host to verify resolution.
  - Check zone serials, ACLs on DNS servers, and firewall rules that may block UDP/TCP 53.
  - For reverse lookup issues, verify PTR records exist in the reverse zone.

---

## Device Security Fundamentals (Beginner)

### Password Types and Hierarchy

Cisco devices use several password types for different access levels:

| Password Type | Purpose | Command |
|--------------|---------|---------|
| Enable Secret | Privileged EXEC access | `enable secret <password>` |
| Enable Password | Legacy (avoid - weak encryption) | `enable password <password>` |
| Console Password | Physical console access | `line console 0` → `password <pass>` |
| VTY Password | Remote telnet/SSH access | `line vty 0 4` → `password <pass>` |
| Auxiliary Password | Aux port access (modems) | `line aux 0` → `password <pass>` |

**Best Practice:** Always use `enable secret` (MD5 hash) instead of `enable password` (Type 7, easily reversed).

### Basic Security Configuration

```
enable
configure terminal

! Set secure enable password
enable secret StrongPass123

! Encrypt all plaintext passwords in config
service password-encryption

! Secure console access
line console 0
 password ConsolePass
 login
 exec-timeout 5 0
 logging synchronous
exit

! Secure VTY (remote) access
line vty 0 4
 password VtyPass
 login
 exec-timeout 10 0
 transport input ssh
exit

! Add login banner
banner motd #
*********************************************
*  AUTHORIZED ACCESS ONLY                   *
*  All activity is logged and monitored     *
*********************************************
#
```

### Verification Commands
- `show running-config | include password` - Check password configuration
- `show line` - View line status and settings
- `show users` - See who is logged in

---

## SSH Configuration (Beginner)

SSH provides encrypted remote access, replacing insecure Telnet.

### Requirements for SSH
1. Hostname must be set (not "Router" or "Switch")
2. Domain name must be configured
3. RSA keys must be generated
4. IOS image must support crypto features

### SSH Configuration Steps

```
! Step 1: Set hostname and domain
hostname R1
ip domain-name company.local

! Step 2: Generate RSA keys (enables SSH)
crypto key generate rsa modulus 2048

! Step 3: Create local user account
username admin privilege 15 secret AdminPass123

! Step 4: Configure VTY lines for SSH
line vty 0 4
 login local
 transport input ssh
exit

! Step 5: Set SSH version 2 (more secure)
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
```

### SSH Verification
- `show ip ssh` - View SSH configuration and version
- `show ssh` - See active SSH sessions
- `show crypto key mypubkey rsa` - View generated keys

---

## CDP and LLDP - Network Discovery (Beginner)

### CDP (Cisco Discovery Protocol)
- **Cisco proprietary** - works only between Cisco devices
- Enabled by default on most Cisco devices
- Operates at Layer 2 (works without IP configuration)
- Sends updates every 60 seconds, holdtime 180 seconds

```
! CDP Commands
show cdp                    ! Check if CDP is enabled
show cdp neighbors          ! Summary of connected devices
show cdp neighbors detail   ! Full details (IP, platform, IOS version)
show cdp interface          ! CDP status per interface

! Enable/Disable CDP
configure terminal
cdp run                     ! Enable globally
no cdp run                  ! Disable globally
interface Gi0/1
 no cdp enable              ! Disable on specific interface
```

### LLDP (Link Layer Discovery Protocol)
- **Industry standard** (IEEE 802.1AB) - works with all vendors
- Disabled by default on Cisco devices
- Similar information to CDP

```
! Enable LLDP
configure terminal
lldp run

! LLDP Commands
show lldp                   ! Check LLDP status
show lldp neighbors         ! Summary of neighbors
show lldp neighbors detail  ! Full neighbor details
```

### Security Note
Disable CDP/LLDP on interfaces facing untrusted networks (Internet, guest networks) to prevent information disclosure.

---

## Port Security (Beginner)

Port security restricts which devices can connect to a switch port by limiting MAC addresses.

### Port Security Configuration

```
! Port security only works on access ports
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 
 ! Enable port security
 switchport port-security
 
 ! Set maximum MAC addresses allowed
 switchport port-security maximum 2
 
 ! Learn MAC addresses automatically and save to config
 switchport port-security mac-address sticky
 
 ! What to do on violation
 switchport port-security violation shutdown
 no shutdown
```

### Violation Modes

| Mode | Action | Counter | Syslog |
|------|--------|---------|--------|
| **shutdown** | Port disabled (err-disabled) | Yes | Yes |
| **restrict** | Drops violating traffic | Yes | Yes |
| **protect** | Drops violating traffic | No | No |

### Recovery from Err-Disabled

```
! Check err-disabled status
show interfaces status | include err

! Re-enable the port
interface GigabitEthernet0/1
 shutdown
 no shutdown
exit

! Or configure automatic recovery
errdisable recovery cause psecure-violation
errdisable recovery interval 300
```

### Verification
- `show port-security` - Overview of all secured ports
- `show port-security interface Gi0/1` - Details for specific port
- `show port-security address` - Learned MAC addresses

---

## Access Control Lists - ACLs (Beginner)

ACLs filter traffic based on criteria like source/destination IP, protocol, and port.

### ACL Types

| Type | Number Range | Filters By |
|------|--------------|------------|
| Standard | 1-99, 1300-1999 | Source IP only |
| Extended | 100-199, 2000-2699 | Source, Dest, Protocol, Port |
| Named | Text name | Same as above |

### Standard ACL Example

```
! Permit network 192.168.1.0/24, deny all else
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any log

! Apply to interface (CLOSE TO DESTINATION)
interface GigabitEthernet0/1
 ip access-group 10 in
```

### Extended ACL Example

```
! Named extended ACL for web traffic
ip access-list extended WEB-ACCESS
 permit tcp 192.168.1.0 0.0.0.255 any eq 80
 permit tcp 192.168.1.0 0.0.0.255 any eq 443
 permit icmp any any echo
 permit icmp any any echo-reply
 deny ip any any log
exit

! Apply to interface (CLOSE TO SOURCE)
interface GigabitEthernet0/0
 ip access-group WEB-ACCESS in
```

### ACL Rules to Remember
1. **Implicit deny all** at the end of every ACL
2. **Order matters** - first match wins
3. Standard ACLs: apply **close to destination**
4. Extended ACLs: apply **close to source**
5. Use **wildcard masks** (inverse of subnet mask)

### Wildcard Mask Quick Reference
| Subnet Mask | Wildcard Mask | Meaning |
|-------------|---------------|---------|
| 255.255.255.255 | 0.0.0.0 | Exact host match |
| 255.255.255.0 | 0.0.0.255 | /24 network |
| 255.255.0.0 | 0.0.255.255 | /16 network |
| 255.0.0.0 | 0.255.255.255 | /8 network |

### ACL Verification
- `show access-lists` - View all ACLs and hit counts
- `show ip interface Gi0/0` - See ACLs applied to interface
- `show running-config | section access-list` - ACLs in config

---

## NTP - Network Time Protocol (Beginner)

Accurate time is critical for logs, certificates, authentication, and troubleshooting.

### NTP Configuration

```
! Set timezone
clock timezone EST -5
clock summer-time EDT recurring

! Configure NTP servers (use multiple for redundancy)
ntp server 216.239.35.0         ! time.google.com
ntp server 216.239.35.4         ! time.google.com backup
ntp server 129.6.15.28          ! NIST time server

! Optional: Use loopback as source
ntp source Loopback0

! Optional: Authenticate NTP (security)
ntp authenticate
ntp authentication-key 1 md5 NtpSecret
ntp trusted-key 1
ntp server 216.239.35.0 key 1
```

### NTP Verification
- `show clock` - Current device time
- `show ntp status` - Sync status and stratum
- `show ntp associations` - NTP server relationships

### Understanding NTP Output
```
R1# show ntp associations

  address         ref clock       st   when   poll reach  delay  offset   disp
*~216.239.35.0   .GOOG.           1     23     64   377   12.5    0.5     1.2
```

| Symbol | Meaning |
|--------|---------|
| * | Synchronized (using this server) |
| + | Candidate for sync |
| - | Not selected |
| ~ | Configured, but not yet synced |

---

## Syslog and Logging (Beginner)

Centralized logging helps with monitoring, security, and troubleshooting.

### Syslog Severity Levels

| Level | Name | Description |
|-------|------|-------------|
| 0 | Emergencies | System unusable |
| 1 | Alerts | Immediate action needed |
| 2 | Critical | Critical conditions |
| 3 | Errors | Error conditions |
| 4 | Warnings | Warning conditions |
| 5 | Notifications | Normal but significant |
| 6 | Informational | Informational messages |
| 7 | Debugging | Debug-level messages |

**Memory trick:** "Every Alley Cat Eats Waffle Nuggets In Doors"

### Logging Configuration

```
! Send logs to syslog server
logging host 192.168.1.100

! Set severity level (6 = informational and above)
logging trap informational

! Use consistent source interface
logging source-interface Loopback0

! Add timestamps to logs
service timestamps log datetime msec localtime show-timezone

! Set local buffer size
logging buffered 16384

! Console logging (be careful with debug)
logging console warnings
```

### Verification
- `show logging` - View logging configuration and buffer
- `show logging | include %` - View log messages only
- `terminal monitor` - See logs on VTY session

---

## Interface Basics and Troubleshooting (Beginner)

### Interface Status Meanings

| Line Status | Protocol Status | Meaning |
|-------------|-----------------|---------|
| up | up | Working correctly |
| up | down | Layer 2 issue (encapsulation, keepalives) |
| down | down | Layer 1 issue (cable, no carrier) |
| administratively down | down | `shutdown` command applied |

### Common Interface Commands

```
! View interface summary
show ip interface brief

! Detailed interface info (errors, speed, duplex)
show interfaces GigabitEthernet0/1

! Layer 3 details (IP, ACLs, NAT)
show ip interface GigabitEthernet0/1

! Switch port status (speed, duplex, VLAN)
show interfaces status
```

### Speed and Duplex Configuration

```
interface GigabitEthernet0/1
 ! Auto-negotiate (recommended)
 speed auto
 duplex auto
 
 ! OR manual settings (both ends must match!)
 speed 1000
 duplex full
 no shutdown
```

### Common Interface Errors

| Counter | Cause | Fix |
|---------|-------|-----|
| CRC errors | Bad cable, EMI interference | Replace cable, check environment |
| Collisions | Duplex mismatch, hub in use | Set duplex correctly, remove hubs |
| Input errors | Layer 1 problems | Check cable, SFP, port |
| Output drops | Congestion, slow interface | QoS, upgrade link |
| Runts | Collisions, bad NIC | Check duplex, replace NIC |
| Giants | Jumbo frames not enabled | Enable jumbo frames or fix MTU |

### Troubleshooting Steps
1. `show ip interface brief` - Is interface up/up?
2. `show interfaces <int>` - Check for errors
3. `show cdp neighbors` - Is neighbor detected?
4. `ping <gateway>` - Layer 3 connectivity
5. `show mac address-table` - Are MACs learned?
6. `show vlan brief` - Correct VLAN assignment?

---

## Loopback Interfaces (Beginner)

Loopback interfaces are virtual interfaces that never go down (unless router is off).

### Use Cases
- **Router ID** for OSPF/BGP (stable identifier)
- **Management access** (always reachable if any path exists)
- **Source for traffic** (NTP, SNMP, logging)
- **Testing** and lab scenarios

### Configuration

```
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 description Router-ID-and-Management
 no shutdown
```

### Best Practices
- Use /32 mask (single host address)
- Number loopbacks consistently across network (Loopback0 for all routers)
- Document loopback address allocation

---

## Configuration Backup and Recovery (Beginner)

### Saving Configuration

```
! Method 1: Full command
copy running-config startup-config

! Method 2: Short command
write memory

! Method 3: Shorthand
wr
```

### Backup to TFTP/FTP

```
! Backup to TFTP
copy running-config tftp:
! Enter IP: 192.168.1.100
! Enter filename: router-config-backup.cfg

! Restore from TFTP
copy tftp: running-config
! Enter IP: 192.168.1.100
! Enter filename: router-config-backup.cfg
```

### View Configuration Differences

```
! Compare running to startup
show archive config differences

! View specific section
show running-config | section interface
show running-config | include hostname
```

### Erasing Configuration (Caution!)

```
! Erase startup configuration
write erase
! or
erase startup-config

! Reload to factory defaults
reload
```

---

## Disabling Unused Ports (Security Best Practice)

Unused switch ports are a security risk. Always disable them.

### Configuration

```
! Create a black-hole VLAN
vlan 999
 name BLACKHOLE_UNUSED
exit

! Disable unused ports and move to black-hole VLAN
interface range GigabitEthernet0/10 - 24
 switchport mode access
 switchport access vlan 999
 shutdown
 description UNUSED-DISABLED
exit
```

### Quick Check for Unused Ports

```
show interfaces status | include notconnect
```

---

## Common Cable Types Reference (Beginner)

| Cable Type | Use Case | Max Length |
|------------|----------|------------|
| **Straight-through** | PC to Switch, Router to Switch | 100m (Cat5e/6) |
| **Crossover** | Switch to Switch, Router to Router (old) | 100m |
| **Rollover (Console)** | PC to Console port (RJ45-DB9) | 3-5m typically |
| **Fiber (Single-mode)** | Long distance, data centers | Up to 10km+ |
| **Fiber (Multi-mode)** | Short distance, within building | 300-550m |

**Note:** Modern switches with Auto-MDIX detect and adjust automatically, making crossover cables rarely needed.

---

## OSI Model Quick Reference (Beginner)

| Layer | Name | Protocols/Devices | PDU |
|-------|------|-------------------|-----|
| 7 | Application | HTTP, DNS, SMTP, FTP | Data |
| 6 | Presentation | SSL/TLS, JPEG, ASCII | Data |
| 5 | Session | NetBIOS, RPC | Data |
| 4 | Transport | TCP, UDP | Segment |
| 3 | Network | IP, ICMP, OSPF, Routers | Packet |
| 2 | Data Link | Ethernet, Switches, MAC | Frame |
| 1 | Physical | Cables, Hubs, NICs | Bits |

**Memory trick:** "All People Seem To Need Data Processing" (top-down)  
**Memory trick:** "Please Do Not Throw Sausage Pizza Away" (bottom-up)

---

## TCP/IP Common Ports (Beginner)

| Port | Protocol | Service |
|------|----------|---------|
| 20-21 | TCP | FTP (data/control) |
| 22 | TCP | SSH |
| 23 | TCP | Telnet |
| 25 | TCP | SMTP (email send) |
| 53 | TCP/UDP | DNS |
| 67-68 | UDP | DHCP (server/client) |
| 69 | UDP | TFTP |
| 80 | TCP | HTTP |
| 110 | TCP | POP3 (email receive) |
| 123 | UDP | NTP |
| 143 | TCP | IMAP |
| 161-162 | UDP | SNMP |
| 443 | TCP | HTTPS |
| 514 | UDP | Syslog |
| 3389 | TCP | RDP |

---

This guide is a concise companion to the in-app Study tab; the game includes quizzes and scenario-based questions to reinforce these commands and patterns.

---

## Lab Scenario: Reach the DNS Server from PC-PT Data

This walkthrough covers every device and command needed so that **PC-PT Data** (VLAN 1 on the left switch) can ping **Server-PT** (VLAN 2 on the right switch) hosting DNS (`192.168.2.10`).

### Switch 1 (left, VLAN separation)
```
enable
configure terminal
vlan 1
 name DATA
vlan 2
 name MANAGEMENT
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 1
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 2
interface GigabitEthernet0/24
 switchport mode trunk
 switchport trunk allowed vlan 1,2
 no shutdown
exit
```

### Router 1 (left router linking VLAN 1 to Router 2)
```
enable
configure terminal
interface GigabitEthernet0/1
 description Link to Switch1
 ip address 192.168.1.3 255.255.255.0
 no shutdown
interface GigabitEthernet0/0
 description Link to Router2
 ip address 10.0.0.1 255.255.255.252
 no shutdown
ip route 192.168.2.0 255.255.255.0 10.0.0.2
ip route 192.168.3.0 255.255.255.0 10.0.0.2
ip route 192.168.4.0 255.255.255.0 10.0.0.2
```

### Router 2 (right, toward DNS server)
```
enable
configure terminal
interface GigabitEthernet0/0
 description Link to Router1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
interface GigabitEthernet0/1
 description Link to Switch2
 ip address 192.168.2.3 255.255.255.0
 no shutdown
interface GigabitEthernet0/2
 description DNS Server VLAN
 ip address 192.168.2.1 255.255.255.0
 no shutdown
ip route 192.168.1.0 255.255.255.0 10.0.0.1
ip route 192.168.3.0 255.255.255.0 10.0.0.1
ip route 192.168.4.0 255.255.255.0 10.0.0.1
```

### Switch 2 (right, server + second PCs)
```
enable
configure terminal
vlan 1
 name DATA
vlan 2
 name MANAGEMENT
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 1
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 2
interface GigabitEthernet0/2
 switchport mode trunk
 switchport trunk allowed vlan 1,2
exit
```

### Server-PT (DNS)
- IP: `192.168.2.10/24`
- Gateway: `192.168.2.1`
- DNS entry: `www.bhclab.edu -> 192.168.2.10`
Enable DNS service and ensure the server responds to ICMP and DNS queries.

### PC-PT Data (VLAN 1)
- IP: `192.168.1.10/24`
- Gateway: `192.168.1.3`
- DNS: `192.168.2.10`
Static or DHCP address; ensure the DHCP pool points to Router1 as gateway and DNS server.

### Verification Commands
```
ping 192.168.2.10       # Server
ping 10.0.0.2           # Router2
nslookup www.bhclab.edu 192.168.2.10
tracert 192.168.2.10    # Windows PC tracing
show ip route           # on both routers
show interfaces status  # on switches
show access-lists       # if ACLs applied
```

Once VLANs, routes, and addresses match the above, PC-PT Data will successfully ping Server-PT and resolve DNS requests through `www.bhclab.edu`.
