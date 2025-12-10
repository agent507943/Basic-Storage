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

This guide is a concise companion to the in-app Study tab; the game includes quizzes and scenario-based questions to reinforce these commands and patterns.
