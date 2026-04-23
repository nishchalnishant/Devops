# Content from CheatSheet_Networking.pdf

## Page 1

Command
Description
ifconfig
Show or configure network interfaces
ifconfig eth0 up
Activate eth0 network interface
ip addr
Show or change IP addresses
ip addr show
Show network interfaces and associated IP addresses
ip addr add 192.168.1.1/24 dev eth0
Add IP address with subnet mask to network
interface
ip link
Show or configure network interfaces
ip link show
Show network interface information
ip link set eth0 down
Deactivate eth0 network interface
ip route
Show or change routing table
ip route show
Show current routing table
ip route add default via <192.168.1.1>
Add default gateway on 192.168.1.1.
Shubham
TrainWith
Shubham
TrainWith
Network_CheatSheet
Cheatsheet for DevOps Engineers
Networking Basics:
Shubham
TrainWith


---

## Page 2

Command
Description
route
Show or configure routing table
route -n
Show routing table (numeric addresses)
route flush
Removes all routes
route add default gw <192.168.1.1>
Add default route to routing table.
arp
Show or change ARP cache
arp -a
Prints arp table
arp -n
Show ARP cache (numeric addresses)
arp -a -d
Deletes all arp table entries
arp -d <192.168.1.100>
Remove 192.168.1.100 from the ARP cache
arp -s
Adds entry in arp table
iwconfig
Manage wireless network interfaces
iwconfig wlan0
Show informationn for wlan0 network interface
curl
wget
Download files from the internet
curl -o <link>
wget <link>
area2 <link>
Download file and save in current directory
Shubham
TrainWith
Advanced Networking:
Shubham
TrainWith
Shubham
TrainWith


---

## Page 3

Network Monitoring:
Command
Description
netstat
Network statistics
netstat -tuln
Show active network sockets
netstat -r
Show kernel routing table
ss
Socket statistics
ss -tuln
Show active network sockets
ss -i
Show network interface packet statistics
iftop
Real time bandwidth usage
iftop -n
Real time bandwidth usage (numeric addresses)
iftop -i eth0
Real time bandwidth usage for eth0 network
interface
tcpdump
Network packet analyzer
tcpdump -i <eth0>
Show network traffic on eth0 network interface
tcpdump -n <port 80>
Show network traffic on port 80 (numeric addresses)
nc / netcat /ncat
Provides the ability to read and write data  across network
connections
hping
Analyzes and exchanges TCP/IP packets with a remote host.
speedometer
Displays bandwidth usage in real-time
vnstat
Logs and shows time-based network traffic stats.
socat
Transfers data between two bidirectional byte streams
Shubham
TrainWith
hubham
ainWith


---

## Page 4

Shubham
TrainWith
DNS and Host Resolution:
Command
Description
dig <example.com>
Perform DNS lookup
nslookup <example.com>
Query DNS servers
host <example.com>
Perform DNS lookup
hostname
Display hostname
hostname <myhost>
Change hostname
DNS and Host Resolution:
Command
Description
ping <example.com>
Send ICMP echo requests
traceroute <example.com>
Trace route to destination
tracepath <example.com>
Simplified traceroute
mtr <example.com>
Combines ping and traceroute functionalities
whois <example.com>
Lookup information for IP or domain.
Connectivity:
Command
Description
ifplugstatus eth0
Check if ethernet cable is plugged in eth0
iperf
Tests network performance within two systems
bwm-ng
Monitors current bandwidth for multiple network interfaces
telnet
Connects to a remote system via Telnet over a TCP/IP
network.
Shubham
TrainWith


---

## Page 5

Shubham
TrainWith
SSH & Remote Access:
Command
Description
ssh
Securely connects to a remote system using the
SSH protocol
scp
Copies files securely between client and server
using the SSH protocol
sftp
Securely transfers files between hosts using the
SFTP protocol
Command
Description
w
Displays information about currently logged-in users
mail
Sends and receives email using the command line.
iw
Displays and configures wireless network interfaces
ngrep
Displays and filters network packet data on a given
regex pattern
Security:
Command
Description
iptables
Firewall utility that manages packet filtering and
NAT.
snort
Intrusion detection system that analyzes network
traffic for suspicious activity
wireshark
Captures and analyzes network traffic in a
formatted text
ufw
Manages system firewall and adds/deletes/modifies/resets
packet filtering rule
Shubham
TrainWith


---

