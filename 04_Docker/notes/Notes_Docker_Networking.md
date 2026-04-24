# Content from Notes_Docker_Networking.pdf

## Page 1

Docker
Networking
Notes 
F O R  D E V O P S  E N G I N E E R S
Train
Train
Shubham
Shubham
With
With


***

## Page 2

Default Bridge Network: The default network in Docker. It creates a
private network on the host machine. Containers connected to the
bridge network can communicate with each other using container names
as hostnames. IP addresses can also be used.
docker run --network=bridge my-container
Docker Networking
Types of Networks in Docker
Train
Train
Shubham
Shubham
With
With
Host Network: With this network mode, containers share the host's
network stack, bypassing network isolation. Containers using the host
network can access services running on the host directly without any
port mapping. This mode can be useful for performance-critical
applications or when network isolation is not a concern.
docker run --network=host my-container


***

## Page 3

Overlay Network: Overlay networks are used for communication
between multiple Docker daemon hosts. This type of network allows
containers running on different hosts to communicate seamlessly as if
they were on the same network. Overlay networks use VXLAN (Virtual
Extensible LAN) encapsulation to achieve network connectivity across
multiple hosts.
docker network create --driver=overlay my-
overlay-network
docker service create --network=my-overlay-
network my-service
Docker Networking
Types of Networks in Docker
Train
Train
Shubham
Shubham
With
With


***

## Page 4

Macvlan Network: Macvlan networks allow containers to have a MAC
address assigned directly to them. This allows containers to appear as
physical devices on the network, enabling them to be assigned IP
addresses from the physical network's subnet. It is particularly useful
when containers require direct Layer 2 network access or when you want
to connect containers directly to external networks.
docker network create -d macvlan --subnet=
<subnet> --gateway=<gateway> -o parent=
<network-interface> my-macvlan-network
docker run --network=my-macvlan-network my-
container
Docker Networking
Types of Networks in Docker
Train
Train
Shubham
Shubham
With
With


***

## Page 5

Custon Bridge Network:  It creates a private network on the host
machine, allowing containers to communicate with each other using
container names as hostnames. Containers connected to the same
bridge network can reach each other via IP addresses.
docker network create my-bridge-network
docker run --network=my-bridge-network my-
container
Docker Networking
Types of Networks in Docker
Train
Train
Shubham
Shubham
With
With
None Network: The none network mode disables networking for a
container. Containers running in this mode have no network interfaces
and are completely isolated from the network. This mode can be useful
when you want to run a container in a fully isolated environment.
docker run --network=none my-container


***

## Page 6

Train
Train
Shubham
Shubham
With
With
Thank You Dosto


