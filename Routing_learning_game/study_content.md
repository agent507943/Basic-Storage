# Advanced IP Routing Learning Guide

## Table of Contents
1. [CIDR and Route Summarization](#cidr-and-route-summarization)
2. [Longest Prefix Match (LPM)](#longest-prefix-match-lpm)
3. [Interior Gateway Protocols (IGPs)](#interior-gateway-protocols-igps)
4. [Border Gateway Protocol (BGP)](#border-gateway-protocol-bgp)
5. [Route Redistribution](#route-redistribution)
6. [Convergence and Timers](#convergence-and-timers)
7. [Policy-Based Routing (PBR)](#policy-based-routing-pbr)
8. [VRFs and Route Leaking](#vrfs-and-route-leaking)
9. [MPLS and Segment Routing](#mpls-and-segment-routing)
10. [Multicast Routing](#multicast-routing)
11. [IPv6 Routing Fundamentals](#ipv6-routing-fundamentals)

---

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

## Border Gateway Protocol (BGP)

### Role of BGP

**BGP** is the Internet’s exterior routing protocol and is also used for large-scale internal designs (iBGP). It scales to millions of routes and supports complex policy.

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

## Multicast Routing

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

Use this guide as a reference while working through the Routing Learning Game. The quiz questions map closely to the sections above, progressing from fundamental definitions to complex design and troubleshooting scenarios.
