# Network Protocols Deep Dive

## DNS (Domain Name System)

### Overview

DNS is the hierarchical, distributed database that translates human-readable domain names to IP addresses.

**Why it matters:** When you type `trainwithshubham.com`, `google.com`, or any domain into a browser, DNS converts it to the IP address that computers actually use to route traffic.

### How DNS Works

```
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌───────┐     ┌────────────┐
│ Client  │────>│  Recursive  │────>│   Root   │────>│  TLD  │────>│   Auth     │
│         │     │  Resolver   │     │   NS     │     │  NS   │     │   NS       │
└─────────┘     └─────────────┘     └──────────┘     └───────┘     └────────────┘
     │                 │                   │               │              │
     │  1. Query       │                   │               │              │
     │  "example.com"  │                   │               │              │
     │────────────────>│                   │               │              │
     │                 │  2. Query         │               │              │
     │                 │──────────────────>│               │              │
     │                 │                   │  3. Referral  │              │
     │                 │                   │  ".com NS"    │              │
     │                 │<──────────────────│               │              │
     │                 │                   │               │              │
     │                 │  4. Query         │               │              │
     │                 │──────────────────────────────────>│              │
     │                 │                   │               │  5. Referral │
     │                 │                   │               │  "example.com│
     │                 │                   │               │<────────────>│
     │                 │                   │               │              │
     │                 │  6. Query         │               │              │
     │                 │─────────────────────────────────────────────────>│
     │                 │                   │               │              │
     │                 │  7. Answer        │               │              │
     │                 │<─────────────────────────────────────────────────│
     │                 │  (IP: 93.184.216.34, TTL: 300)    │              │
     │                 │                   │               │              │
     │  8. Answer      │                   │               │              │
     │<────────────────│                   │               │              │
```

### DNS Query Types

| Type | Description | Example |
|------|-------------|---------|
| **Recursive** | DNS server must reply with the final answer or an error | Client asks resolver for `google.com` — resolver does all the work |
| **Iterative** | Client follows referrals until it finds the answer | Resolver queries root → TLD → authoritative |
| **Non-Recursive** | Server responds from cache or authoritative data | Cached response, no additional queries needed |

### DNS Record Types

| Record Type | Purpose | Example |
|-------------|---------|---------|
| **A** | Maps domain to IPv4 address | `example.com → 93.184.216.34` |
| **AAAA** | Maps domain to IPv6 address | `example.com → 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Canonical name (alias) | `www.example.com → example.com` |
| **MX** | Mail exchange server | `10 mail.example.com` |
| **TXT** | Arbitrary text (SPF, DKIM, verification) | `"v=spf1 include:_spf.google.com ~all"` |
| **NS** | Nameserver for the domain | `example.com → ns1.example.com` |
| **PTR** | Reverse DNS (IP → domain) | `34.216.184.93.in-addr.arpa → example.com` |
| **SOA** | Start of Authority (zone metadata) | Serial, refresh, retry, expire, minimum TTL |
| **SRV** | Service location | `_http._tcp.example.com` |
| **CAA** | Certificate Authority Authorization | Limits which CAs can issue certs |

### DNS Caching

**Why caching matters:**
- Large sites like Google have people accessing from all over the globe
- Same domain name may resolve to different IPs based on geography
- DNS caching reduces latency and load on DNS servers

**TTL (Time to Live) Strategy:**
| TTL Value | Use Case | Trade-off |
|-----------|----------|-----------|
| 60-300s | Fast failover, frequent changes | High query load on authoritative servers |
| 3600-86400s | Stable records, low query volume | Slow propagation of changes |

**Migration Pattern:**
1. Lower TTL to 60s at least 24 hours before the change
2. Make the DNS change
3. Restore TTL to normal value

### DNS Commands

```bash
# Query DNS (modern, detailed output)
dig example.com
dig example.com ANY
dig @8.8.8.8 example.com  # Use specific DNS server

# Query DNS (simple output)
host example.com

# Query DNS (legacy, still useful)
nslookup example.com

# Check DNS propagation
dig +trace example.com  # Shows full resolution path
```

***

## DHCP (Dynamic Host Configuration Protocol)

### Overview

DHCP is a network administration protocol that automatically assigns IP addresses and TCP/IP configuration to devices on a network.

**RFC:** 2131

**Layer:** Application Layer (uses UDP ports 67/68)

### Why Use DHCP?

**Without DHCP:**
- Manual IP configuration for each device
- Must manually reclaim IPs when devices leave
- Error-prone, time-consuming

**With DHCP:**
- Automated, centralized IP management
- Dynamic (leased) addresses — returned to pool when unused
- No user setup required to join the network

### DHCP Server Configuration

A DHCP server maintains a database containing:

| Configuration Item | Description |
|--------------------|-------------|
| **Valid IP range** | Pool of addresses available for distribution |
| **Excluded addresses** | IPs reserved and not distributed |
| **Reservations** | Specific IP → MAC mappings (consistent assignment) |
| **Lease duration** | How long an IP can be used before renewal |
| **Subnet mask** | Network segmentation information |
| **Default gateway** | Router address for outbound traffic |
| **DNS servers** | Name resolution servers |
| **Domain name** | DNS suffix for the network |

### How DHCP Works (DORA Process)

```
┌─────────┐                              ┌─────────┐
│  Client │                              │  Server │
└────┬────┘                              └────┬────┘
     │                                        │
     │  1. DISCOVER (Broadcast)               │
     │  "I need an IP address"                │
     │  UDP 68 → UDP 67                       │
     │───────────────────────────────────────>│
     │                                        │
     │  2. OFFER (Unicast/Broadcast)          │
     │  "I can offer you 192.168.1.100"       │
     │  Includes: IP, mask, gateway, DNS, TTL │
     │<───────────────────────────────────────│
     │                                        │
     │  3. REQUEST (Broadcast)                │
     │  "I accept 192.168.1.100"              │
     │  (broadcast so other servers know)     │
     │───────────────────────────────────────>│
     │                                        │
     │  4. ACK (Unicast)                      │
     │  "Confirmed, here are your settings"   │
     │<───────────────────────────────────────│
     │                                        │
     │  5. Client configures interface        │
     │                                        │
```

**DORA:** **D**iscover → **O**ffer → **R**equest → **A**cknowledge

### Lease Renewal

- **T1 timer (50% of lease):** Client sends unicast REQUEST to original server
- **T2 timer (87.5% of lease):** Client broadcasts REQUEST if T1 fails
- **Lease expired:** Client must restart DORA process

### DHCP Commands

```bash
# Linux - Release and renew
dhclient -r  # Release
dhclient     # Renew

# Check DHCP lease
cat /var/lib/dhcp/dhclient.leases

# Windows
ipconfig /release
ipconfig /renew

# View current DHCP settings
ipconfig /all  # Windows
ifconfig       # Linux/macOS
```

***

## SSH (Secure Shell)

### Overview

SSH is a protocol for securely accessing remote computers via command-line interaction.

**Port:** 22 (default)

**Replaces:** Telnet, rlogin, rsh (all insecure)

### Why SSH?

| Feature | Benefit |
|---------|---------|
| **Encryption** | All traffic encrypted with strong ciphers |
| **Authentication** | Password or public-key based |
| **Integrity** | Data cannot be modified in transit |
| **Security** | Protects against DNS spoofing, IP source routing, IP spoofing |

### SSH Protocol Architecture

```
┌─────────────────────────────────────────────┐
│         SSH Protocol Stack                  │
├─────────────────────────────────────────────┤
│  Connection Layer                           │
│  (Multiplexes multiple sessions)            │
├─────────────────────────────────────────────┤
│  User Authentication Layer                  │
│  (Password, Public-key, keyboard-interactive)│
├─────────────────────────────────────────────┤
│  Transport Layer                            │
│  (Encryption, compression, integrity)       │
└─────────────────────────────────────────────┘
```

#### Transport Layer
- Manages initial key exchange
- Server identification
- Encryption and compression
- Integrity checking
- Interface for transmitting/receiving messages (up to 32,768 bytes)

#### User Authentication Layer
- Client identification
- Multiple authentication methods:

| Method | Description |
|--------|-------------|
| **Password** | Simple password verification, optional password change |
| **Public-key** | DSA, ECDSA, or RSA keypairs |
| **keyboard-interactive** | Server sends prompts, client responds (used for OTP) |
| **GSSAPI** | External authentication (Kerberos 5, NTLM) for single sign-on |

#### Connection Layer
- Specifies routes for SSH services
- Handles channels, channel requests, global requests
- Multiple channels over one SSH connection
- Bidirectional data flow

**Channel Types:**
| Type | Purpose |
|------|---------|
| **shell** | Interactive shell, SFTP, exec commands |
| **direct-tcpip** | Client-to-server port forwarding |
| **forwarded-tcpip** | Server-to-client port forwarding |

### SSH Commands

```bash
# Basic connection
ssh user@hostname
ssh user@192.168.1.100

# Specify port
ssh -p 2222 user@hostname

# Use specific identity file
ssh -i ~/.ssh/id_rsa user@hostname

# Port forwarding (local)
ssh -L 8080:localhost:80 user@hostname

# Port forwarding (remote)
ssh -R 8080:localhost:80 user@hostname

# Execute remote command
ssh user@hostname 'ls -la'

# Copy SSH key to remote host
ssh-copy-id user@hostname

# Verbose mode (troubleshooting)
ssh -v user@hostname
ssh -vvv user@hostname  # More verbose
```

### SSH Config File (~/.ssh/config)

```
Host production
    HostName prod.example.com
    User admin
    IdentityFile ~/.ssh/prod_key
    Port 2222

Host staging
    HostName staging.example.com
    User deploy
    ForwardAgent yes
```

***

## SCP (Secure Copy Protocol)

### Overview

SCP aids in the secure transmission of computer data from a local to a remote host.

**Port:** 22

**Based on:** RCP (Remote Copy Protocol) + SSH (for authentication and encryption)

### SCP vs CP

| Feature | CP | SCP |
|---------|----|-----|
| **Scope** | Local filesystem only | Local ↔ Remote or Remote ↔ Remote |
| **Security** | None (local only) | Encrypted via SSH |
| **Authentication** | N/A | SSH authentication required |
| **Permissions** | Preserved | Preserved (with -p flag) |

### SCP Command Syntax

```bash
scp [-32658BCpqrv] [-c cipher] [-F ssh_config] [-i identity_file]
    [-l limit] [-o ssh_option] [-P port] [-S program]
    [[user@]SRC_host:]file1 ... [[user@]DEST_host:]file2
```

### SCP Options

| Option | Description |
|--------|-------------|
| `-c cipher` | Select cipher for encryption (passed to SSH) |
| `-F ssh_config` | Alternative SSH config file |
| `-i identity_file` | Identity (key) file for authentication |
| `-l limit` | Bandwidth limit in Kbps |
| `-o ssh_option` | Pass options to SSH (same format as ssh_config) |
| `-P port` | Port to connect on (capital P) |
| `-p` | Preserve access/modification times and modes |
| `-q` | Quiet mode (disable progress meter) |
| `-r` | Copy directories recursively |
| `-S program` | Program for encrypted connection (must understand SSH options) |
| `-v` | Verbose mode (debugging) |
| `-3` | Copy between two remote hosts via local host |
| `-6` | Use IPv6 |
| `-B` | Batch mode (no passwords) |
| `-C` | Enable compression |

### SCP Usage Examples

```bash
# Upload file to remote host
scp /local/file.txt user@remote:/remote/path/

# Download file from remote host
scp user@remote:/remote/file.txt /local/path/

# Upload directory recursively
scp -r /local/dir user@remote:/remote/path/

# Specify port
scp -P 2222 file.txt user@remote:/path/

# Preserve timestamps and permissions
scp -p file.txt user@remote:/path/

# Limit bandwidth (1000 Kbps)
scp -l 1000 largefile.tar.gz user@remote:/path/

# Copy between two remote hosts (via local)
scp -3 user1@host1:/path/file.txt user2@host2:/path/

# Use specific identity file
scp -i ~/.ssh/id_rsa file.txt user@remote:/path/
```

### SCP vs Alternatives

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| **SCP** | Simple secure copy | Built-in, easy | No resume, being deprecated |
| **SFTP** | Interactive file transfer | Resume support, file management | Slightly more complex |
| **rsync** | Efficient sync | Delta transfer, resume | More complex syntax |
| **FTP** | Legacy file transfer | Widely supported | Insecure (plaintext) |

**Note:** OpenSSH 9.0+ deprecated SCP in favor of SFTP. Modern alternative:
```bash
# Instead of scp, use sftp with batch mode
sftp user@host <<EOF
put file.txt /remote/path/
EOF
```

***

## cURL (Client URL)

### Overview

cURL is a command-line utility for transferring data between a device and a server using various protocols.

**Powered by:** libcurl (portable client-side URL transfer library)

### Supported Protocols

| Protocol | Description |
|----------|-------------|
| **HTTP/HTTPS** | Web requests (default) |
| **FTP/FTPS** | File Transfer Protocol |
| **SFTP** | SSH File Transfer Protocol |
| **SMTP/SMTPS** | Email sending |
| **POP3/POP3S** | Email retrieval |
| **IMAP/IMAPS** | Email access |
| **LDAP/LDAPS** | Directory services |
| **DICT** | Dictionary lookup |
| **FILE** | Local file access |
| **SMB/SMB2** | Windows file sharing |
| **MQTT** | IoT messaging |
| **RTSP** | Real-time streaming |

### Common Use Cases

- Downloading files from the internet
- Endpoint testing (API development)
- Debugging HTTP issues
- Error logging
- Automation scripts

### Basic Syntax

```bash
curl [options] [URL]
```

### cURL Options

| Option | Description |
|--------|-------------|
| `-o <file>` | Save output to file |
| `-O` | Save output with original filename |
| `-X <method>` | Specify HTTP method (GET, POST, PUT, DELETE) |
| `-H <header>` | Add HTTP header |
| `-d <data>` | Send data in POST request |
| `-u <user:pass>` | Authentication credentials |
| `-k` | Allow insecure SSL connections |
| `-L` | Follow redirects |
| `-s` | Silent mode |
| `-v` | Verbose output |
| `-I` | Fetch headers only (HEAD request) |
| `--limit-rate` | Limit transfer speed |
| `-C -` | Resume partial download |

### cURL Examples

```bash
# Simple GET request
curl https://example.com

# Save to file
curl -O https://example.com/file.zip
curl -o myfile.html https://example.com

# Multiple URLs
curl -O http://url1.com/file1.html -O http://url2.com/file2.html

# URL pattern matching
curl http://example.{page1,page2,page3}.html

# POST request with data
curl -X POST -d "name=John&email=john@example.com" https://api.example.com/users

# POST JSON
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"John","email":"john@example.com"}' \
     https://api.example.com/users

# Add custom headers
curl -H "Authorization: Bearer TOKEN" \
     -H "Accept: application/json" \
     https://api.example.com/data

# Upload file via FTP
curl -T localfile.txt "ftp://target-destination/"

# Send email via SMTP
curl smtp://smtp.example.com \
     --mail-from sender@example.com \
     --mail-rcpt receiver@example.com \
     --upload-file email.txt

# Dictionary lookup
curl "dict://dict.org/d:hello"

# Test endpoint with verbose output
curl -v https://api.example.com/health

# Follow redirects
curl -L https://example.com

# Silent mode (for scripts)
curl -s https://example.com

# Show only HTTP status code
curl -s -o /dev/null -w "%{http_code}" https://example.com
```

### cURL for API Testing

```bash
# GET with query parameters
curl "https://api.example.com/users?page=1&limit=10"

# PUT request
curl -X PUT -H "Content-Type: application/json" \
     -d '{"id":1,"name":"Updated"}' \
     https://api.example.com/users/1

# DELETE request
curl -X DELETE https://api.example.com/users/1

# With authentication
curl -u username:password https://api.example.com/protected

# With client certificate (mTLS)
curl --cert client.crt --key client.key https://api.example.com

# Rate-limited download
curl --limit-rate 100k https://example.com/largefile.zip

# Resume interrupted download
curl -C - -O https://example.com/largefile.zip
```

***

## FTP (File Transfer Protocol)

### Overview

FTP is a network protocol for transmitting files between computers over TCP/IP connections.

**Layer:** Application Layer

**Ports:** 20 (data), 21 (control)

### FTP Architecture

- **Local host:** End user's computer (client)
- **Remote host:** Server providing FTP services
- **Control connection:** Port 21, commands and responses
- **Data connection:** Port 20, actual file transfer

### FTP Modes

| Mode | Description |
|------|-------------|
| **Active** | Server initiates data connection to client |
| **Passive** | Client initiates data connection to server (firewall-friendly) |

### FTP Commands

```bash
# Command-line FTP
ftp ftp.example.com

# Using cURL for FTP
curl -u username:password ftp://ftp.example.com/file.txt
curl -T localfile.txt ftp://ftp.example.com/

# Using cURL for FTPS (FTP over SSL)
curl --ssl ftps://ftp.example.com/file.txt
```

### Security Note

**FTP transmits data (including passwords) in plaintext.** Use SFTP or FTPS for secure file transfer.

***

## Protocol Port Reference

| Protocol | Port(s) | Transport | Layer | Description |
|----------|---------|-----------|-------|-------------|
| HTTP | 80 | TCP | 7 | Hypertext Transfer Protocol |
| HTTPS | 443 | TCP | 7 | HTTP over TLS |
| FTP | 20/21 | TCP | 7 | File Transfer Protocol |
| SSH | 22 | TCP | 7 | Secure Shell |
| Telnet | 23 | TCP | 7 | Remote terminal (insecure) |
| SMTP | 25 | TCP | 7 | Simple Mail Transfer |
| SMTPS | 465 | TCP | 7 | SMTP over TLS |
| DNS | 53 | TCP+UDP | 7 | Domain Name System |
| DHCP | 67/68 | UDP | 7 | Dynamic Host Configuration |
| TFTP | 69 | UDP | 7 | Trivial File Transfer |
| HTTP Alt | 8080 | TCP | 7 | Common alternate HTTP |
| NTP | 123 | UDP | 7 | Network Time Protocol |
| SNMP | 161/162 | UDP | 7 | Network management |
| LDAP | 389 | TCP | 7 | Directory services |
| HTTPS-alt | 8443 | TCP | 7 | Alternate HTTPS |
| IMAPS | 993 | TCP | 7 | IMAP over TLS |
| MySQL | 3306 | TCP | 7 | MySQL database |
| PostgreSQL | 5432 | TCP | 7 | PostgreSQL database |
| Redis | 6379 | TCP | 7 | Redis in-memory store |
| MongoDB | 27017 | TCP | 7 | MongoDB database |
| Kubernetes API | 6443 | TCP | 7 | Kubernetes control plane |
| etcd | 2379-2380 | TCP | 7 | etcd cluster |

***

## Summary: Key Protocol Takeaways

| Protocol | Primary Use | Key Feature |
|----------|-------------|-------------|
| DNS | Name resolution | Hierarchical distributed database |
| DHCP | IP address assignment | DORA process, dynamic leases |
| SSH | Secure remote access | Encryption, public-key auth |
| SCP | Secure file copy | SSH-based, being deprecated |
| cURL | Data transfer | Multi-protocol, scripting |
| FTP | File transfer | Legacy, insecure (use SFTP/FTPS) |
