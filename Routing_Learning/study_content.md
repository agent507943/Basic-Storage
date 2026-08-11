# Routing Learning Guide

This guide merges the foundational routing curriculum with the advanced IP routing reference into a single study resource. Part 1 covers fundamentals through modern technologies; Part 2 goes deeper on CIDR, BGP, redistribution, convergence, VRFs, MPLS, multicast, and IPv6.

## Table of Contents

**Part 1 — Routing Fundamentals to Modern Technologies**
1. [Introduction to Routing](#introduction-to-routing)
2. [Routing Fundamentals](#routing-fundamentals)
3. [Static vs Dynamic Routing](#static-vs-dynamic-routing)
4. [Routing Metrics and Administrative Distance](#routing-metrics-and-administrative-distance)
5. [Distance Vector Routing Protocols](#distance-vector-routing-protocols)
6. [Link State Routing Protocols](#link-state-routing-protocols)
7. [Hybrid Routing Protocols](#hybrid-routing-protocols)
8. [Exterior Gateway Protocols](#exterior-gateway-protocols)
9. [Advanced Routing Concepts](#advanced-routing-concepts)
10. [Routing Security](#routing-security)
11. [Network Design and Scalability](#network-design-and-scalability)
12. [Troubleshooting Routing Issues](#troubleshooting-routing-issues)
13. [IPv6 Routing](#ipv6-routing)
14. [Modern Routing Technologies](#modern-routing-technologies)

**Part 2 — Advanced IP Routing Reference**
15. [CIDR and Route Summarization](#cidr-and-route-summarization)
16. [Longest Prefix Match (LPM)](#longest-prefix-match-lpm)
17. [Interior Gateway Protocols (IGPs)](#interior-gateway-protocols-igps)
18. [Border Gateway Protocol (BGP) Deep Dive](#border-gateway-protocol-bgp-deep-dive)
19. [Route Redistribution](#route-redistribution)
20. [Convergence and Timers](#convergence-and-timers)
21. [Policy-Based Routing (PBR)](#policy-based-routing-pbr)
22. [VRFs and Route Leaking](#vrfs-and-route-leaking)
23. [MPLS and Segment Routing](#mpls-and-segment-routing)
24. [Multicast Routing Deep Dive](#multicast-routing-deep-dive)
25. [IPv6 Routing Fundamentals](#ipv6-routing-fundamentals)

---

# Part 1 — Routing Fundamentals to Modern Technologies

## Introduction to Routing

**Routing** is the process of selecting paths across one or more networks and forwarding data packets from a source to a destination through multiple network segments. It operates at Layer 3 (Network Layer) of the OSI model and is fundamental to internetworking.

### Key Concepts
- **Router**: A network device that forwards packets between different networks
- **Routing Table**: A database containing network destinations and the best paths to reach them
- **Next Hop**: The IP address of the next router in the path to a destination
- **Convergence**: When all routers agree on the best paths to network destinations
- **Hop**: Each router traversed in the path from source to destination

### Why Routing Matters
- **Internetwork Connectivity**: Enables communication between different network segments
- **Path Optimization**: Selects the best paths based on various metrics
- **Fault Tolerance**: Provides alternative paths when primary routes fail
- **Load Distribution**: Can balance traffic across multiple paths
- **Scalability**: Enables networks to grow without redesigning the entire infrastructure

## Routing Fundamentals

### How Routing Works
1. **Packet Reception**: Router receives a packet with destination IP address
2. **Routing Table Lookup**: Router searches routing table for best matching route
3. **Next Hop Determination**: Identifies the next router in the path
4. **Packet Forwarding**: Sends packet to the next hop
5. **TTL Decrement**: Decreases Time-To-Live to prevent infinite loops

### Routing Table Components
- **Destination Network**: The network or host to reach
- **Next Hop**: IP address of the next router
- **Metric**: Cost or preference for the route
- **Administrative Distance**: Trustworthiness of the route source
- **Interface**: Outgoing interface to reach the next hop
- **Route Source**: How the route was learned (static, protocol, connected)

### Types of Routes
- **Connected Routes**: Directly attached networks (AD = 0)
- **Static Routes**: Manually configured routes (AD = 1)
- **Dynamic Routes**: Learned through routing protocols
- **Default Route**: Catch-all route (0.0.0.0/0) for unknown destinations

### Longest Prefix Match
Routers use the most specific (longest prefix) route that matches the destination. For example:
- 192.168.1.0/24 is more specific than 192.168.0.0/16
- 0.0.0.0/0 (default route) matches everything but has lowest priority

## Static vs Dynamic Routing

### Static Routing

**Characteristics:**
- Manually configured by network administrators
- Routes don't change unless manually modified
- Simple configuration for small, stable networks
- No routing protocol overhead

**Advantages:**
- Predictable routing behavior
- No CPU overhead for route calculations
- Complete administrative control
- No routing protocol authentication needed
- Suitable for stub networks

**Disadvantages:**
- No automatic adaptation to topology changes
- Difficult to maintain in large networks
- Manual intervention required for failures
- Prone to human configuration errors

**Use Cases:**
- Small networks with stable topology
- Stub networks with single exit point
- Default routes to ISP
- Backup routes for redundancy

### Dynamic Routing

**Characteristics:**
- Routes learned automatically through routing protocols
- Adapts to network topology changes
- Protocols exchange routing information between routers
- Automatic convergence after network changes

**Advantages:**
- Automatic adaptation to network changes
- Faster recovery from failures
- Scalable for large networks
- Load balancing capabilities
- Reduced administrative overhead

**Disadvantages:**
- CPU and memory overhead
- Network bandwidth consumption
- Complex configuration and troubleshooting
- Potential security vulnerabilities
- Convergence time considerations

**Use Cases:**
- Large enterprise networks
- Networks with redundant paths
- Dynamic network topologies
- Internet service provider networks

## Routing Metrics and Administrative Distance

### Administrative Distance (AD)
Administrative Distance determines the trustworthiness of routing information sources. Lower AD values are preferred.

**Common AD Values:**
- Connected: 0
- Static: 1
- EIGRP Internal: 90
- OSPF: 110
- RIP: 120
- EIGRP External: 170
- eBGP: 20
- iBGP: 200

### Routing Metrics
When multiple routes to the same destination exist with the same AD, metrics determine the best path.

**Common Metrics:**
- **Hop Count**: Number of routers to destination (RIP)
- **Bandwidth**: Link capacity (EIGRP, IGRP)
- **Delay**: Time to traverse the path (EIGRP, IGRP)
- **Cost**: Administrative value based on link characteristics (OSPF)
- **Reliability**: Link error rates (EIGRP, IGRP)
- **Load**: Link utilization (EIGRP, IGRP)
- **MTU**: Maximum transmission unit size

## Distance Vector Routing Protocols

Distance vector protocols learn routes by distance (metric) and vector (direction/next hop).

### Routing Information Protocol (RIP)

**Characteristics:**
- Uses hop count as metric (max 15 hops)
- Updates every 30 seconds
- Split horizon and poison reverse for loop prevention
- Simple configuration and operation

**RIP Timers:**
- Update Timer: 30 seconds
- Invalid Timer: 180 seconds
- Hold-down Timer: 180 seconds
- Flush Timer: 240 seconds

**RIP Versions:**
- **RIPv1**: Classful, no authentication, broadcast updates
- **RIPv2**: Classless, authentication support, multicast updates
- **RIPng**: IPv6 version of RIP

**Loop Prevention Mechanisms:**
- **Split Horizon**: Don't advertise routes back through the interface learned
- **Route Poisoning**: Advertise failed routes with infinite metric (16)
- **Poison Reverse**: Explicitly advertise poisoned routes
- **Hold-down Timers**: Prevent premature acceptance of new routes

**Advantages:**
- Simple configuration
- Low CPU requirements
- Suitable for small networks
- Vendor interoperability

**Disadvantages:**
- Limited to 15 hops
- Slow convergence
- Inefficient bandwidth usage
- No load balancing
- Vulnerable to routing loops

### Enhanced Interior Gateway Routing Protocol (EIGRP)

**Characteristics:**
- Cisco proprietary (open standard since 2013)
- Advanced distance vector (hybrid)
- Uses composite metric based on bandwidth and delay
- Fast convergence using DUAL algorithm
- Support for VLSM and CIDR

**EIGRP Components:**
- **Neighbor Table**: Adjacent EIGRP routers
- **Topology Table**: All routes to destinations
- **Routing Table**: Best routes (successors)

**Key Concepts:**
- **Successor**: Best route to destination
- **Feasible Successor**: Loop-free backup route
- **Feasible Distance (FD)**: Best metric from local router
- **Advertised Distance (AD)**: Metric from neighbor to destination
- **Feasibility Condition**: AD < FD for loop-free paths

**EIGRP Metric Calculation:**
```
Metric = 256 * [K1*BW + ((K2*BW)/(256-Load)) + K3*Delay + K4*(Reliability/(255-K5*Reliability))]
Default: K1=K3=1, K2=K4=K5=0
Simplified: 256 * (BW + Delay)
```

**DUAL Algorithm:**
- Diffusing Update Algorithm
- Guarantees loop-free paths
- Fast convergence using backup routes
- Queries for new paths when needed

**EIGRP Packet Types:**
- Hello: Neighbor discovery and maintenance
- Update: Routing information exchange
- Query: Request for routing information
- Reply: Response to queries
- Acknowledge: Reliable packet confirmation

**Advanced Features:**
- **Variance**: Load balancing across unequal-cost paths
- **Summarization**: Manual route aggregation
- **Authentication**: MD5 and SHA authentication
- **Graceful Shutdown**: Controlled route removal

## Link State Routing Protocols

Link state protocols maintain complete network topology and use shortest path algorithms.

### Open Shortest Path First (OSPF)

**Characteristics:**
- Open standard link state protocol
- Uses Dijkstra's shortest path first algorithm
- Hierarchical design with areas
- Fast convergence through immediate LSA flooding
- Support for VLSM and CIDR

**OSPF Areas:**
- **Backbone Area (Area 0)**: Central area connecting all others
- **Standard Areas**: Regular OSPF areas
- **Stub Areas**: Don't receive external LSAs
- **Totally Stubby Areas**: Only receive default route
- **Not-So-Stubby Areas (NSSA)**: Allow limited external routes

**OSPF LSA Types:**
- **Type 1 (Router LSA)**: Router's links within an area
- **Type 2 (Network LSA)**: Multi-access network information
- **Type 3 (Summary LSA)**: Inter-area routes
- **Type 4 (ASBR Summary)**: Location of ASBR
- **Type 5 (External LSA)**: External routes
- **Type 7 (NSSA External)**: External routes in NSSA areas

**OSPF Network Types:**
- **Point-to-Point**: No DR/BDR election needed
- **Broadcast**: DR/BDR election required
- **Non-Broadcast Multi-Access (NBMA)**: Manual neighbor configuration
- **Point-to-Multipoint**: Treats NBMA as collection of point-to-point

**Designated Router (DR) Election:**
1. Highest OSPF priority (0-255)
2. Highest router ID (if priority tied)
3. DR election is not preemptive

**OSPF Metric Calculation:**
- Cost = Reference Bandwidth / Interface Bandwidth
- Default reference bandwidth: 100 Mbps
- Can be manually configured per interface

**OSPF Authentication:**
- Area authentication (all routers in area)
- Interface authentication (per link)
- Types: Simple password, MD5, SHA

### Intermediate System to Intermediate System (IS-IS)

**Characteristics:**
- ISO standard link state protocol
- Dual-stack support (IP and CLNS)
- Two-level hierarchy (Level 1 and Level 2)
- TLV-based extensible format

**IS-IS Levels:**
- **Level 1**: Intra-area routing
- **Level 2**: Inter-area routing
- **Level 1-2**: Both intra and inter-area

**Advantages over OSPF:**
- Better scalability
- Easier area design
- Faster convergence in some scenarios
- Better support for traffic engineering

## Hybrid Routing Protocols

### Enhanced Interior Gateway Routing Protocol (EIGRP)
EIGRP combines distance vector and link state features:

**Distance Vector Characteristics:**
- Exchanges routing tables with neighbors
- Uses metrics for path selection
- Bellman-Ford algorithm basis

**Link State Characteristics:**
- Maintains topology table
- Fast convergence using backup routes
- Loop-free path guarantees

**Unique Features:**
- **Reliable Transport Protocol (RTP)**: Ensures delivery of critical updates
- **Bounded Updates**: Only sends changes, not complete tables
- **Unequal Cost Load Balancing**: Traffic distribution across multiple paths

## Exterior Gateway Protocols

### Border Gateway Protocol (BGP)

**Characteristics:**
- Path vector protocol for inter-AS routing
- The routing protocol of the Internet
- Policy-based routing with extensive attributes
- TCP-based for reliable communication (port 179)

**BGP Types:**
- **eBGP**: Between different autonomous systems
- **iBGP**: Within the same autonomous system

**BGP Attributes:**
- **Well-known Mandatory**: AS_PATH, ORIGIN, NEXT_HOP
- **Well-known Discretionary**: LOCAL_PREF, ATOMIC_AGGREGATE
- **Optional Transitive**: AGGREGATOR, COMMUNITY
- **Optional Non-transitive**: MED, ORIGINATOR_ID

**BGP Path Selection Process:**
1. Highest LOCAL_PREF
2. Shortest AS_PATH
3. Lowest ORIGIN (IGP < EGP < Incomplete)
4. Lowest MED (if same AS)
5. eBGP over iBGP
6. Lowest IGP metric to NEXT_HOP
7. Oldest route
8. Lowest BGP router ID

**BGP Route Types:**
- **Customer Routes**: Highest preference
- **Peer Routes**: Medium preference
- **Provider Routes**: Lowest preference

**BGP Scaling Solutions:**
- **Route Reflection**: Reduces iBGP mesh requirements
- **Confederations**: Divides AS into sub-ASes
- **Route Filtering**: Controls route advertisement

**BGP Security:**
- **RPKI**: Resource Public Key Infrastructure
- **Route Origin Validation (ROV)**: Verify route origins
- **BGPsec**: Path validation (future standard)

## Advanced Routing Concepts

### Route Summarization/Aggregation
Combining multiple network routes into a single advertisement:

**Benefits:**
- Reduces routing table size
- Decreases routing update traffic
- Improves convergence time
- Hides network instability

**Types:**
- **Auto-summarization**: Automatic at classful boundaries
- **Manual summarization**: Administrator-configured
- **Default routing**: Ultimate summarization (0.0.0.0/0)

### Equal Cost Multi-Path (ECMP)
Load balancing across multiple equal-cost routes:

**Benefits:**
- Increased bandwidth utilization
- Improved redundancy
- Better network performance

**Implementation:**
- OSPF: Up to 16 equal-cost paths
- EIGRP: Up to 16 equal-cost paths (32 with variance)
- BGP: Multiple path support

### Policy-Based Routing (PBR)
Routing based on criteria other than destination:

**Applications:**
- Traffic engineering
- QoS implementation
- Security policies
- Load balancing

### Virtual Routing and Forwarding (VRF)
Multiple routing table instances on single router:

**Uses:**
- MPLS VPNs
- Internet and private network separation
- Multi-tenancy support

### Multicast Routing
Forwarding traffic from one source to multiple destinations:

**Protocols:**
- **PIM-SM**: Protocol Independent Multicast Sparse Mode
- **PIM-DM**: Protocol Independent Multicast Dense Mode
- **MSDP**: Multicast Source Discovery Protocol

## Routing Security

### Common Threats

#### Route Hijacking
Unauthorized announcement of IP prefixes:
- **Impact**: Traffic redirection, interception, denial of service
- **Detection**: BGP monitoring, RPKI validation
- **Mitigation**: Route filtering, RPKI deployment

#### Man-in-the-Middle Attacks
Intercepting and potentially modifying routing information:
- **Impact**: Traffic interception, data manipulation
- **Prevention**: Routing protocol authentication, encrypted tunnels

#### Denial of Service (DoS)
Overwhelming routing infrastructure:
- **Types**: Route table exhaustion, convergence attacks
- **Mitigation**: Rate limiting, resource protection

### Security Mechanisms

#### Authentication
- **Simple Authentication**: Plain text passwords (weak)
- **Cryptographic Authentication**: MD5, SHA hashing
- **Digital Signatures**: RSA, ECDSA for BGP

#### Route Filtering
- **Prefix Lists**: Filter routes by network address
- **AS Path Filters**: Filter based on AS path attributes
- **Community Filters**: Filter using BGP communities

#### TTL Security
Generalized TTL Security Mechanism (GTSM):
- Verifies packets come from directly connected neighbors
- Prevents attacks from distant sources

#### Routing Protocol Authentication
- **OSPF**: Area and interface authentication
- **EIGRP**: Key chain authentication
- **BGP**: TCP MD5 authentication
- **RIP**: Key chain authentication

### Best Practices

#### Network Design
- Implement hierarchical routing design
- Use route summarization appropriately
- Deploy redundant paths with proper metrics
- Implement proper area/AS boundaries

#### Security Implementation
- Enable routing protocol authentication
- Implement route filtering policies
- Deploy RPKI where applicable
- Monitor routing table changes
- Use secure management practices

## Network Design and Scalability

### Hierarchical Design
Three-layer model for scalable networks:

**Core Layer:**
- High-speed backbone connectivity
- Minimal route manipulation
- Fast convergence focus

**Distribution Layer:**
- Route summarization and filtering
- Policy implementation
- Inter-VLAN routing

**Access Layer:**
- End device connectivity
- Default routing to distribution

### Area Design Principles

#### OSPF Areas
- Keep areas manageable (< 50 routers)
- Implement proper summarization at ABRs
- Use stub areas to reduce LSA flooding
- Design redundant ABRs for fault tolerance

#### EIGRP Autonomous Systems
- Implement proper summarization
- Use appropriate hello/hold timers
- Design query boundaries to prevent SIA

### Route Summarization Strategy
- Summarize at area/AS boundaries
- Use contiguous address blocks
- Balance specificity vs. efficiency
- Consider impact on traffic engineering

## Troubleshooting Routing Issues

### Common Problems

#### Routing Loops
**Symptoms:** Intermittent connectivity, high CPU usage
**Causes:** Incorrect metrics, redistribution issues
**Solutions:** Verify routing tables, check metrics, implement loop prevention

#### Convergence Issues
**Symptoms:** Slow recovery from failures
**Causes:** Large convergence domains, poor timers
**Solutions:** Optimize areas/AS, tune timers, implement summarization

#### Suboptimal Routing
**Symptoms:** Traffic taking longer paths
**Causes:** Incorrect metrics, redistribution issues
**Solutions:** Adjust metrics, verify path selection

### Diagnostic Tools

#### Show Commands
- `show ip route`: Display routing table
- `show ip protocols`: Show routing protocol information
- `show ip ospf database`: OSPF topology database
- `show ip bgp`: BGP routing table

#### Debug Commands
- `debug ip routing`: Routing table changes
- `debug ip ospf events`: OSPF events
- `debug ip eigrp`: EIGRP information
- `debug ip bgp updates`: BGP updates

#### Network Analysis
- Packet captures with Wireshark
- SNMP monitoring
- NetFlow analysis
- Routing protocol analyzers

### Troubleshooting Methodology
1. **Identify symptoms** and scope of problem
2. **Gather information** using show/debug commands
3. **Isolate the issue** to specific protocol or area
4. **Analyze routing tables** and protocol databases
5. **Check physical connectivity** and interface status
6. **Verify configuration** against design requirements
7. **Implement solution** and verify resolution
8. **Document findings** and prevention measures

## IPv6 Routing

### IPv6 Address Types
- **Unicast**: One-to-one communication
- **Multicast**: One-to-many communication
- **Anycast**: One-to-nearest communication

### IPv6 Routing Protocols

#### OSPFv3
- IPv6 version of OSPF
- Similar LSA types with IPv6 addressing
- Authentication via IPsec

#### EIGRP for IPv6
- Separate process from IPv4 EIGRP
- Similar operation with IPv6 addressing

#### RIPng
- IPv6 version of RIP
- UDP port 521
- Hop count limitation remains

#### MP-BGP
- Multiprotocol extensions for BGP
- Supports IPv6 and other address families
- Address family specific configuration

### IPv6 Transition Mechanisms
- **Dual Stack**: Running IPv4 and IPv6 simultaneously
- **Tunneling**: IPv6 over IPv4 (6to4, 6in4, 6rd)
- **Translation**: NAT64, DNS64

## Modern Routing Technologies

### Software-Defined Networking (SDN)
Centralized network control plane:
- **Controller**: Centralized routing decisions
- **Southbound APIs**: Communication with network devices
- **Northbound APIs**: Application interfaces

### Segment Routing
Source-based routing using segment identifiers:
- **SR-MPLS**: MPLS-based implementation
- **SRv6**: IPv6-based implementation
- **Benefits**: Simplified network design, traffic engineering

### MPLS Traffic Engineering
Explicit path control for traffic optimization:
- **LSPs**: Label Switched Paths
- **RSVP-TE**: Resource reservation protocol
- **LDP**: Label distribution protocol

### Network Function Virtualization (NFV)
Virtualizing network functions including routing:
- **Virtual routers**: Software-based routing
- **Service chaining**: Combining virtual functions
- **Orchestration**: Automated deployment and management

---

# Part 2 — Advanced IP Routing Reference

## CIDR and Route Summarization

### What is CIDR?

**Classless Inter-Domain Routing (CIDR)** replaces the old classful addressing model and allows variable-length subnet masks. Instead of being limited to fixed classes (A, B, C), networks are expressed as *prefix/length* pairs such as `10.1.0.0/16` or `192.168.10.0/24`.

### Benefits of CIDR
- **Flexible subnetting**: Design prefixes that match real topology and address needs
- **Reduced routing table size**: Summarize many specific routes into a single aggregate
- **Better address utilization**: Avoid wasting large blocks just to get a particular prefix size

### Route Summarization (Aggregation)
- **Definition**: Combining multiple more-specific routes into a single summary prefix
- **Example**: `10.10.0.0/24` through `10.10.3.0/24` can be summarized as `10.10.0.0/22`
- **Benefits**:
  - Smaller routing tables
  - Faster convergence
  - Less control-plane churn across the network

### Design Considerations
- Summaries must align on binary boundaries
- Summaries should not hide more-specific routes that need distinct policies
- Poorly planned summarization can cause blackholes if certain subnets are missing behind a summarizing router

---

## Longest Prefix Match (LPM)

Routers forward IP packets based on **longest prefix match**:

- The router checks all routes whose prefix matches the destination IP
- Among all matching routes, the one with the **longest prefix length** (most bits) is chosen
- Only if prefix lengths are equal do metrics and administrative distances matter

### Example
Available routes:
- `10.0.0.0/8`
- `10.10.0.0/16`
- `10.10.1.0/24`
- `10.10.1.128/25`

Destination: `10.10.1.130`

All four prefixes match, but the **/25** is most specific, so the router forwards using `10.10.1.128/25`.

### Operational Impact
- Policy and security should consider that more-specific routes override summaries
- Route leaks or accidental more-specifics can attract traffic unexpectedly
- Consistent prefix planning is critical in large networks

---

## Interior Gateway Protocols (IGPs)

### Common IGPs
- **OSPF (Open Shortest Path First)** – Link-state, supports areas, widely used
- **IS-IS (Intermediate System to Intermediate System)** – Link-state, popular in large SP cores
- **EIGRP** – Advanced distance-vector/hybrid (traditionally Cisco proprietary)
- **RIP/RIPv2** – Legacy distance-vector, hop-count metric, rarely used in modern designs

### Link-State vs Distance-Vector
- **Link-State**:
  - Routers flood topology information (LSAs/LSPs)
  - Each router builds a full map of the network and runs SPF
  - Faster convergence, more scale, but more complex
- **Distance-Vector**:
  - Routers exchange reachability and metrics to destinations
  - Simpler but more prone to loops and slower convergence

### OSPF Areas
- **Backbone Area (0)**: All other areas must connect to it
- **Regular (Standard) Areas**: Full LSAs, no restrictions
- **Stub / Totally Stubby Areas**: Limit external LSAs to reduce size
- **NSSA (Not-So-Stubby Area)**: Allows limited external injection via Type 7 LSAs

Careful area design and summarization are key to scalable IGP deployments.

---

## Border Gateway Protocol (BGP) Deep Dive

### Role of BGP

**BGP** is the Internet's exterior routing protocol and is also used for large-scale internal designs (iBGP). It scales to millions of routes and supports complex policy.

### Key Attributes
- **LOCAL_PREF**: Influences outbound path selection inside an AS (higher is preferred)
- **AS-PATH**: Sequence of AS numbers the route has traversed (shorter is usually preferred)
- **MED (Multi-Exit Discriminator)**: Suggests entry points into an AS (lower is preferred)
- **Origin, Communities, Next-hop**: Additional attributes for more granular policy

### Path Selection (Simplified)
Typical sequence (varies by vendor, simplified):
1. Highest LOCAL_PREF
2. Shortest AS-PATH
3. Lowest origin type (IGP over EGP over Incomplete)
4. Lowest MED (when comparing paths from the same neighboring AS)
5. eBGP over iBGP
6. Lowest IGP metric to BGP next hop

### Traffic Engineering
- **Outbound**: Change LOCAL_PREF or choose different exit points
- **Inbound**: AS-PATH prepending, selective advertisement, communities, MED

Good BGP design requires clear policies, filtering, and strict prefix controls.

---

## Route Redistribution

### What is Redistribution?

Redistribution allows one routing domain (e.g., EIGRP) to inject its routes into another (e.g., OSPF). It is often used during migrations or at boundaries between different protocols.

### Risks
- **Routing Loops**: When protocols re-learn their own routes after redistribution
- **Metric Mismatch**: Different metric types require careful translation
- **Route Explosion**: Too many redistributed prefixes can overwhelm IGPs

### Best Practices
- Use **one-way redistribution** where possible
- Filter routes explicitly (prefix lists, route-maps)
- Summarize at redistribution points to reduce detail
- Tag redistributed routes to prevent re-import into their source protocol

---

## Convergence and Timers

### Convergence

**Convergence** is the time it takes the network to reach a consistent view after a change or failure.

Key components:
- **Failure detection** – hello and dead timers, BFD
- **Control-plane processing** – SPF calculations, route selection
- **FIB updates** – programming hardware forwarding tables

### Timers
- **Hello Timer**: How often a routing protocol sends hello packets
- **Dead/Hold Timer**: How long without hellos before a neighbor is declared down
- **BFD (Bidirectional Forwarding Detection)**: Fast failure detection independent of the routing protocol

Tuning timers can significantly reduce convergence time but increases control-plane load and sensitivity to transient loss.

### Micro-Loops
When convergence is very fast or inconsistent across routers, transient **micro-loops** can form. Mitigation techniques include:
- Loop-free alternates (LFA)
- Ordered FIB updates
- Careful summarization and hierarchy

---

## Policy-Based Routing (PBR)

### Concept

PBR allows forwarding decisions to be based on **policies** other than destination IP alone. Examples:
- Source address
- Application ports
- DSCP/ToS bits
- Incoming interface

### Use Cases
- Steering critical applications over low-latency links
- Directing backup or bulk traffic over cheaper paths
- Implementing special handling for specific tenants or customers

### Caveats
- Can override normal routing and cause drops if the policy next hop fails
- Must be integrated with tracking (e.g., IP SLA) for reliability
- Adds complexity compared to pure destination-based routing

---

## VRFs and Route Leaking

### VRFs

**Virtual Routing and Forwarding (VRF)** instances hold separate routing tables on a single device:
- Enable multi-tenancy or strong segmentation
- Prevent overlapping IP spaces from conflicting
- Common in MPLS VPNs and VRF-lite enterprise designs

### Route Leaking
- **Definition**: Intentionally sharing selected routes between VRFs or between VRF and global table
- **Methods**:
  - Static routes pointing between VRFs
  - Route-target import/export in MPLS VPNs
  - PBR or policy-based mechanisms

### Design Concerns
- Only leak what is necessary to minimize attack surface
- Understand symmetry—traffic must have a valid return path
- Consider overlapping prefixes when interconnecting previously isolated networks

---

## MPLS and Segment Routing

### MPLS Basics

**Multiprotocol Label Switching (MPLS)** uses short labels instead of IP prefixes for data-plane forwarding:
- Labels are pushed, swapped, or popped along an LSP (Label Switched Path)
- Enables L2/L3 VPNs, traffic engineering, and fast reroute

### Key Roles
- **Ingress LSR**: Pushes labels based on FEC (Forwarding Equivalence Class)
- **Transit LSR**: Swaps labels
- **Egress LSR**: Pops labels and forwards based on IP

### Segment Routing (SR)

SR encodes a list of **segments** (instructions) in the packet:
- Node segments – represent routers
- Adjacency segments – represent specific links
- Service segments – represent functions or chains

SR-MPLS uses the MPLS label stack; SRv6 uses IPv6 extension headers.

---

## Multicast Routing Deep Dive

### Concepts
- **One-to-many or many-to-many** communication
- Uses **multicast groups** instead of broadcast
- Efficient distribution only to interested receivers

### Protocols
- **IGMP/MLD** – Receiver membership signaling
- **PIM-SM / PIM-SSM** – Multicast routing in the core
- **RP (Rendezvous Point)** – Meeting point for sources and receivers in PIM-SM

### RPF (Reverse Path Forwarding)
- Router checks that multicast traffic arrives on the interface it would use to reach the source
- Prevents loops and duplicates

### Design Points
- Choose RP placement carefully
- Consider switching from shared tree to SPT for performance
- Monitor group membership and usage

---

## IPv6 Routing Fundamentals

### Address Types
- **Global Unicast** – Routable on the Internet (e.g., 2000::/3)
- **Link-Local** – FE80::/10, used on a single link for neighbor discovery
- **Unique Local (ULA)** – FC00::/7, private addressing for internal use
- **Multicast** – FF00::/8, replaces most IPv4 broadcast functions

### Neighbor Discovery
- Uses ICMPv6 messages instead of ARP
- Relies heavily on multicast groups (solicited-node, all-nodes, all-routers)

### Transition and Coexistence
- **Dual-stack** – Run IPv4 and IPv6 in parallel
- **Tunneling** – 6to4, GRE, DMVPN and others for transport
- **Translation** – NAT64 and related mechanisms for IPv4/IPv6 interoperability

### Design Considerations
- Plan addressing and summarization just as with IPv4
- Watch for overlapping ULA prefixes when interconnecting sites
- Ensure routing protocols (OSPFv3, IS-IS, BGP) are correctly enabled for IPv6

---

Use this guide alongside the interactive Routing Learning app to reinforce your understanding, progressing from fundamental definitions through complex design and troubleshooting scenarios.
