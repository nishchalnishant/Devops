# Content from networking_for_devops.pdf

## Page 1

Networking For Devops 
 
Index 
1.​ Basic Networking Concepts 
a.​ IP Addressing (IPv4 & IPv6) 
b.​ Subnetting and CIDR 
c.​ Ports and Protocols 
d.​ OSI and TCP/IP models 
2.​ Network Infrastructure and Topologies 
a.​ Routers, Switches, and Hubs 
b.​ VLANs, NAT, and VPN 
c.​ Load Balancers 
d.​ Firewalls and Security Groups 
e.​ DNS and Service Discovery 
3.​ Cloud Networking 
a.​ Virtual Private Cloud (VPC) 
b.​ Subnets and Route Tables 
c.​ Content Delivery Networks (CDN) 
4.​ Network Automation 
a.​ Infrastructure as Code (IaC) 
b.​ Network Configuration Tools 
c.​ CI/CD for Network Configuration 
5.​ Service Discovery and Distributed Systems 
a.​ Tools and Services 
b.​ Service Meshes 
6.​ Container Networking 
a.​ Docker Networking 
b.​ Kubernetes Networking 
7.​ Monitoring, Logging, and Tracing 
a.​ Network Monitoring Tools 
b.​ Network Logging 
c.​ Network Tracing 
8.​ Network Security 
a.​ Encryption 
b.​ Intrusion Detection and Prevention Systems (IDS/IPS) 
c.​ Zero Trust Architectures 
9.​ Performance and Optimization 
a.​ Bandwidth and Latency Considerations 
b.​ Traffic Shaping and QoS (Quality of Service) 
10.​Software Defined Networking (SDN) 
 
 
 


---

## Page 2

1. Basic Networking Concepts 
IP Addressing (IPv4 & IPv6) 
 
●​ Understanding IP Addresses: Every device connected to the internet is assigned a 
unique IP address. IPv4, the most common, is a 32-bit address format, written in decimal 
as four numbers separated by periods. Each number can be 0-255. IPv6, a 128-bit 
address, was introduced to address IPv4 exhaustion.​
Example: An IPv4 address looks like 192.0.2.146, while an IPv6 might resemble 
2001:0db8:85a3:0000:0000:8a2e:0370:7334.​
Real-world scenario: Imagine if houses didn't have addresses. How would you deliver a 
letter? Similarly, devices use IP addresses to send and receive data. 
Subnetting and CIDR 
●​ Why Subnetting?: It's like dividing a city into neighborhoods. By segmenting a network 
into subnets, broadcast traffic is contained, network security and performance are 
improved. 
●​ CIDR: Stands for Classless Inter-Domain Routing. CIDR notation provides an efficient 
way to represent IP addresses and their associated routing prefix.​
CIDR, or "supernetting", is a method to allocate IP addresses more efficiently. By using 
CIDR, we can reduce the number of wasted IP addresses, making IPv4's life longer than 
initially anticipated.​


---

## Page 3

Example: 192.168.1.0/24. Here, 192.168.1.0 is the network address, and /24 indicates 
the first 24 bits are the network prefix.​
Real-world scenario: A university might use different subnets for its administration, 
faculty, students, and guests to manage network resources effectively. 
Ports and Protocols 
●​ Ports: Computers use port numbers to determine to which process it should deliver 
incoming data. Ports range from 0 to 65535. 
●​ Protocols: Rules that define the data format and transmission for communication.​
Example: HTTP operates on port 80, HTTPS on port 443.​
Real-world scenario: Imagine the IP address as the address of a huge commercial 
building, and the port as a particular office number or floor. The building address gets 
you to the building, but the office number directs you to the exact location. 
OSI and TCP/IP models 
 
●​ Why Layers?: To simplify networking functions and allow interoperability between 
different products and software. OSI has 7 layers, while TCP/IP usually uses 4. 
​
OSI was conceptual and never really implemented. TCP/IP, on the other hand, became 
the de facto standard. Understanding these models helps grasp the separation of 
concerns, from physical transmission of data (Layer 1) up to application-level protocols 
like HTTP or FTP (Layer 7 in OSI, Layer 4 in TCP/IP). 
​
Example: When you visit a website, the request travels through multiple OSI layers - 
from your browser (application layer) through the internet (network layer) and finally 
reaching the website server (data link and physical layers).​
Real-world scenario: Consider the process of mailing a physical letter. Writing the letter 
is akin to the Application Layer, putting it in an envelope relates to the Transport Layer, 
and sending it through the postal system parallels the Network Layer. 
2. Network Infrastructure and Topologies 
Routers, Switches, and Hubs 
 
●​ Definition: These devices help in directing and managing traffic. Routers connect 
networks (like your home network to your ISP). Switches operate within a network, 
directing data to the right device. Hubs, now mostly outdated, just broadcast data to 
every device.​
The real distinction is about intelligence and data handling. Hubs are "dumb" - they blast 
data to all connected devices. Switches are smarter; they learn the MAC addresses of 


---

## Page 4

connected devices and "switch" data to the correct device. Routers operate at a higher 
layer; they're concerned with routing data between different networks. 
​
Example: A common home setup includes a modem (connecting to the ISP) and a router 
(distributing the internet connection to various devices). 
​
Real-world scenario: If the internet is a vast highway system, routers are the major 
intersections, switches are the smaller intersections, and hubs are open marketplaces 
where everyone hears what's said. 
VLANs, NAT, and VPN 
●​ VLANs (Virtual Local Area Networks): They are used to segment a larger physical 
network into smaller virtual networks based on function, department, or other criteria. 
●​ NAT (Network Address Translation): Transforms public IP addresses into private (and 
vice versa) allowing multiple devices to share a single public IP. 
●​ VPN (Virtual Private Network): Encrypted tunnel across the internet that allows secure 
access to a private network from a remote location. 
●​ VLANs can help segment network traffic without requiring separate physical 
infrastructures. NAT, meanwhile, is crucial for conserving global IPv4 addresses. VPNs 
ensure private communication over the public internet.​
Example: A NAT device might be your home router. When you browse a website, the 
router transforms your private IP address to its public one (and back) so you can 
communicate with the outside world.​
Real-world scenario: Think of NAT as apartment mailboxes. Everyone has a unique 
mailbox (private IP), but the mail carrier only sees one address for the entire building 
(public IP). VPNs, on the other hand, are like private, secure courier services that only 
deliver to specific locations. 
Load Balancers 
●​ Function: They distribute incoming traffic among multiple servers, ensuring no single 
server is overwhelmed, leading to optimal resource use and minimizing response time.​
Example: Websites with high traffic, like Amazon during a sale, utilize load balancers to 
ensure smooth user experience.​
Real-world scenario: Imagine a popular restaurant. A single waiter can't serve every 
customer. Load balancers are like the manager who assigns customers to various 
waiters to balance the workload.​
 
Firewalls and Security Groups 
 


---

## Page 5

●​ Function: Firewalls monitor and control incoming and outgoing traffic based on 
predetermined security policies. Security groups are a cloud version, applied to a set of 
resources. 
​
Example: A company firewall might block access to social media during work hours. In 
AWS, you can set a security group rule to allow traffic only from a specific IP.​
Real-world scenario: A firewall is like a security checkpoint at the entrance of a building, 
ensuring only authorized people can enter or exit.​
 
DNS and Service Discovery 
●​ DNS (Domain Name System): Converts human-friendly URLs into IP addresses. 
●​ Service Discovery: In microservices architectures, services dynamically discover and 
communicate with one another without a fixed IP.​
 
●​ Example: Entering www.google.com into a browser. DNS servers convert it to something 
like 172.217.5.110.​
Real-world scenario: DNS is like a phonebook. Instead of searching for a person's phone 
number, you look up their name. Service Discovery is akin to a dynamic phonebook that 
automatically updates when people change their numbers. 
3. Cloud Networking 
Virtual Private Cloud (VPC) 
 
●​ Function: VPC provides an isolated, private section of the cloud where you can launch 
resources in a defined virtual network.​
In a multi-tenant cloud environment, this ensures your resources aren't accessible to 
others by default. VPCs often come with private and public subnets, allowing 


---

## Page 6

fine-grained control over resource accessibility.​
Example: An organization might use a VPC to create a private, isolated section of the 
AWS Cloud where they can launch AWS resources, such as EC2 instances, in a virtual 
network that they define. 
 
Subnets and Route Tables 
 
●​ Subnets: Divides the IP address range of a VPC. They can span multiple Availability 
Zones (AZs) for high availability. 
●​ Route Tables: Contain rules (routes) that determine where network traffic is directed. 
Route tables define how traffic should flow between subnets and outside the VPC.​
Example 1: Within a VPC, you could have a public subnet for web servers that have 
direct access to the internet and a private subnet for backend systems like databases or 
application servers that shouldn't be directly accessed from the internet.​
Example 2: Say you have an application spread across two AZs for redundancy. Each 
AZ will have its own subnet. Route tables ensure that if one AZ fails, traffic is rerouted to 
the healthy AZ.​
Code Snippet (Creating a subnet with Terraform in AWS): 
 
Content Delivery Networks (CDN) 
 
●​ Function: CDNs store cached content on edge servers in various locations, allowing 
faster content delivery to users based on their geographic location.​
Beyond caching, they offer DDoS mitigation, bot protection, and even serverless function 


---

## Page 7

execution.​
Example: If a user in Paris visits a US-based website, a CDN could serve the website's 
static content from an edge server located in Europe rather than the US, reducing 
latency. 
4. Network Automation 
Infrastructure as Code (IaC) 
 
●​ Definition: A method where infrastructure is provisioned and managed using code. With 
version control, automated testing, and CI/CD, infrastructure becomes more reliable and 
agile.​
Example: Using Terraform, one can define infrastructure components within 
configuration files and apply those files to provision real-world infrastructure elements in 
cloud environments.​
 
Network Configuration Tools 
●​ Function: These tools can automate the configuration and management of network 
devices. In large organizations with diverse equipment, ensuring consistent 
configurations is crucial. These tools push consistent configurations to devices, often 
integrating with version control for rollback capabilities. 
​
Example: Ansible can be used to push configurations to network devices. Instead of 


---

## Page 8

logging into each device individually, you can define the configuration once and have 
Ansible apply it to all devices.​
Example: After a major network overhaul, configurations across 200 switches need 
updating. Rather than manual updates, a tool like Ansible pushes the new configuration, 
with consistency checks and rollback options if anything goes wrong.​
 
CI/CD for Network Configuration 
●​ Definition: Continuously integrating and deploying network configurations using 
automated pipelines. Just as CI/CD revolutionized software delivery, it's doing the same 
for network configurations. Automated testing ensures only valid configurations are 
pushed, and rollbacks happen if issues arise.​
Example: Jenkins, a popular CI/CD tool, can be set up to listen for changes in your 
network configuration repository. When changes are detected, Jenkins can run tests to 
ensure the validity of configurations and then deploy them to your devices. 


---

## Page 9

5. Service Discovery and Distributed Systems 
 
Tools and Services 
●​ Definition: In a distributed environment, especially with microservices, the number of 
services can be large, dynamic, and decentralized. Service discovery tools help keep 
track of these services, their locations, health, and metadata.​
Example: Consul is a tool that provides service discovery, configuration, and 
orchestration capabilities. When a new service instance is launched (due to scaling or 
fault recovery), it registers with Consul. Other services query Consul to find this instance 
and communicate with it.​
 
Service Meshes 
●​ Function: Service meshes manage how different parts of an application share data with 
one another. They provide features like traffic management, service discovery, routing, 


---

## Page 10

load balancing, security, failure recovery, metrics, and monitoring.​
Example: Istio is a popular service mesh tool. With Istio, if Service A wants to 
communicate with Service B, the request goes through Istio, which applies traffic rules, 
handles load balancing, retries, and more before sending the request to Service B.​
 
●​ Containers encapsulate an application and its dependencies, allowing it to run 
consistently across various computing environments. But, ensuring these containers can 
communicate efficiently and securely is a challenge. This section talks about how these 
containers communicate. 
Docker Networking 
 
●​ Function: Docker uses different networking modes to allow communication between 
containers and with external networks, like, from host (where the container shares the 
host's networking) to bridge (where a private internal network is created) to overlay (for 
multi-host communication in clusters).​
Example: Docker's bridge network mode is the default networking mode, isolating 
containers from each other and the host, yet allowing them to communicate. 
Kubernetes Networking 
 
●​ Function: Kubernetes, a container orchestration platform, has its own set of networking 
principles. Every pod in a Kubernetes cluster gets its IP, and pods can seamlessly 
communicate with one another, and nodes can communicate with all pods, without NAT. 
These requirements ensure transparent communication in clustered environments.​


---

## Page 11

Use Case: When rolling out a new version of your app in Kubernetes, the old and new 
versions might run simultaneously. Kubernetes networking ensures seamless 
communication between old and new pods, regardless of which node they're on.​
Example: To expose a set of pods to external traffic, Kubernetes uses a Service of type 
LoadBalancer.​
 
●​ Monitoring, Logging, and Tracing: With vast, distributed architectures in place, keeping 
an eye on the health, performance, and errors in the system becomes paramount. 
Network Monitoring Tools 
●​ Function: These tools continuously keep an eye on the network, measuring performance 
metrics and checking for failures. Beyond just uptime checks, advanced tools can predict 
outages based on trends, auto-discover devices in your infrastructure, and integrate with 
alerting systems for real-time notifications.​
Example: A spike in traffic might risk overwhelming a server. Monitoring tools detect the 
trend and can trigger auto-scaling, spawning new server instances to handle the load. 
Network Logging 
●​ Definition: This involves capturing logs related to network activities, which can be crucial 
for diagnostics and audits. These logs provide a granular view of network activities, vital 
for postmortem analyses after incidents. When integrated with AI-driven analytics, they 
can even offer predictive insights.​
Example: Syslog servers collect logs from various devices. These logs might be 
forwarded to platforms like the ELK stack (Elasticsearch, Logstash, Kibana) for 
visualization and analysis. 
Network Tracing 
●​ Function: Tracing tools assist in capturing the life of a request as it travels through 
various services, helping diagnose issues. It offers a "breadcrumb trail" of a request. In 
distributed systems, understanding how a request flows can help pinpoint bottlenecks 
and failures.​
Use Case: Users complain of slow-loading reports. Tracing reveals that a particular 
microservice takes unusually long to respond, highlighting a performance bottleneck.​
Example: traceroute can show the path a packet takes through the network. In 
microservices, tools like Jaeger or Zipkin can provide end-to-end request tracing. 
8. Network Security 
As threats evolve, so must our defense strategies. Beyond just preventing unauthorized access, 
modern network security is about visibility, adaptability, and rapid response. 


---

## Page 12

Encryption 
●​ Function: Encryption transforms data into a coded form, ensuring only someone with the 
correct key can decipher it. Protocols like TLS are continuously evolving, with older, 
vulnerable versions being deprecated.​
Use Case: GDPR and other data protection regulations mandate stringent data security 
measures. Encrypting data in transit between your data center and end-users ensures 
compliance.​
Example: SSL/TLS, which is used by HTTPS, encrypts data transferred between the 
web server and the client. 
Intrusion Detection and Prevention Systems (IDS/IPS) 
 
●​ Function: These systems continuously monitor network traffic, looking for patterns or 
signatures that match known malicious activities.​
Example: Tools like Snort can be configured to block or alert on suspicious activities. 
Zero Trust Architectures 
 
●​ Definition: Traditional security operated under "trust but verify." Zero trust turns this on its 
head – "never trust, always verify." Every request, internal or external, is treated as 
potentially hostile.​


---

## Page 13

Use Case: An employee's credentials are compromised. However, because of zero trust, 
the attacker can't access sensitive systems. Every request they make is challenged and 
verified, preventing data breaches.​
Example: Google's BeyondCorp is a well-known implementation of the Zero Trust model. 
9. Performance and Optimization 
A fast, responsive network isn't just about bandwidth. It's about smart traffic management, 
prioritization, and ensuring data takes the most efficient path. 
Bandwidth and Latency Considerations 
 
●​ Bandwidth: The maximum data transfer rate of a network. Higher bandwidth means 
more data can be transferred simultaneously.​
Latency: The delay before a data transfer starts following an instruction for its transfer.​
While bandwidth is about volume, latency is about speed. A high-bandwidth connection 
might still feel slow if latency is high. Reducing the number of "hops" a data packet must 
make, and ensuring efficient routing can mitigate this.​
Use Case: A cloud-based application feels sluggish to users in Australia. By deploying 
an instance in the Asia-Pacific region and using smart DNS routing, users are directed to 
the nearest instance, drastically reducing latency. 
Traffic Shaping and QoS (Quality of Service) 
●​ Function: With diverse traffic types on networks, from VoIP calls to file backups to 
real-time gaming, ensuring each gets its due is a challenge. Traffic shaping and QoS 
tools can prioritize traffic, allocate bandwidth, and even schedule certain activities during 
off-peak times. These techniques prioritize certain types of traffic over others, ensuring 
crucial applications get the resources they need.​
Use Case: In a corporate network, VoIP calls are prioritized during business hours, 
ensuring crystal-clear audio. Backup activities, which are bandwidth-intensive but not 
time-sensitive, are scheduled for nighttime. 


---

## Page 14

10. Software Defined Networking (SDN) 
SDN decouples the network control plane from the data-forwarding plane, providing more 
flexibility and programmability to network configurations. Traditional networks, defined by 
physical hardware and static configurations, struggled to keep pace with dynamic, cloud-based 
deployments. SDN abstracts away the hardware layer, allowing for virtualized, programmable 
networks. 
Use Case: A sudden marketing campaign goes viral, leading to an unpredictable surge in traffic. 
An SDN solution can auto-adjust, provisioning more resources, rerouting traffic to avoid 
congestion, and ensuring users get a seamless experience. 
 


---

