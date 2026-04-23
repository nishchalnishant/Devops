# Content from DevOps_Roadmap_V4.pdf

## Page 1

DEVOPS
ROADMAP
created by  


---

## Page 2

We already successfully guided 10,000s of our students
from zero DevOps know-how to becoming
Senior DevOps and Cloud Engineers
#1 Educator for
DevOps & Cloud Engineering
Download our detailed Syllabus
If you too, want to become a highly-paid and confident
DevOps and Cloud engineer, then
to see how we guarantee your
career transformation
or copy link: 
https://www.techworld-with-nana.com/devops-
bootcamp#devops-curriculum-and-projects


---

## Page 3

TABLE OF CONTENTS
I. START HERE
4
17
18
19
20
21
28
29
II. DEVOPS ROADMAP
III. STARTING FROM...
Systems Administrator
Software Developer
Test Automation Engineer
Network Engineer
No or Little IT Background
V. RECAP AND RESOURCES
Summary - DevOps Roadmap
TWN DevOps and Cloud Resources
D E V O P S  R O A D M A P  B Y
T E C H W O R L D  W I T H  N A N A
W W W . T E C H W O R L D - W I T H - N A N A . C O M
5-14
IV. DEVOPS CAREER PATHS
DevOps and Cloud Engineer
SRE and Platform Engineer
DevSecOps and MLOps Engineer
24
25
26


---

## Page 4

Start Here
This is a step by step path I would take as a DevOps professional and educator, if
I was starting from zero again. Showing you what would be the most efficient
path to become a DevOps engineer based on the knowledge that I have now.
I hope with this I can help you in this highly rewarding, but challenging journey
into DevOps.
And I wanted to make it more individual for you
based on your background from which you are
transitioning into DevOps:
system administrator
software developer
test automation engineer
network engineer
someone with zero or very little IT knowledge
So after the DevOps roadmap, you will find
information on how to start in DevOps having any
of these backgrounds.
One important thing beforehand:
Since DevOps covers the whole software development lifecycle, it
means you work with lots of technologies. Plus DevOps is still
evolving and there are lots of new tools being developed all the
time.
So you have to be comfortable with constantly learning and
expanding your knowledge, even after you have become a DevOps
engineer.


---

## Page 5

01
Concepts of Software
Development
As a DevOps engineer you will not be
programming the application, but as
you are working closely with the
development team to improve and
automate tasks for them, you need to
understand the concepts of:
www.techworld-with-nana.com/devops-roadmap
And generally understand what the
whole software development lifecycle
covers from idea to code, all the way to
releasing it to the end users!
How developers work and
collaborate
(Agile, Jira workflows)
What Git workflow
they use
How applications are
configured (Build &
Packaging Tools)
Automated testing and
test scopes


---

## Page 6

You also need to know the basics of
Networking & Security in order to
configure the infrastructure, like:
Configure Firewalls to secure access
Understand how IP addresses, ports
and DNS works
Load Balancers
Proxies
HTTP/HTTPS
As a DevOps engineer you are
responsible for preparing and
maintaining the infrastructure (servers)
on which the application is deployed.
So you need to know the basics of how
to administer a server and install
different tools on it.
Basic concepts of Operating Systems
you need to understand:
Since most servers use Linux OS, you
need to know  and feel comfortable
using Linux, especially its Command
Line Interface.
02
OS & Linux Basics
Shell Commands
Linux File System & Permissions
SSH Key Management
Virtualization
However, to draw a line here between DevOps and IT Operations: You don't
need to be the SysAdmin. So no advanced knowledge of server
administration is needed here. It's enough to know the basics. There are own
professions like SysAdmins, Networking or Security Professionals for more
advanced use cases.
www.techworld-with-nana.com/devops-roadmap


---

## Page 7

Some things you should know:
Run containers
Inspect active containers
Docker Networking
Persist data with Docker Volumes
Dockerize apps using Dockerfiles
Run multiple containers using
Docker-Compose
Work with Docker Repository
As containers have become the new
standard of software packaging, you will
run your application as a container.
This means you need to generally
understand:
concepts of virtualization 
concepts of containerization
how to manage containerized
applications on a server.
Docker is by far the most popular
container technology!
03
Containerization - Docker
Containers and virtual machines have similar resource isolation and allocation
benefits, but function differently. VMs virtualize the whole OS. Containers
virtualize only the application level of the OS. Therefore, containers are more
lightweight and faster.
A container is a
standard unit of
software that
packages up code and
all its dependencies,
so the application runs quickly and
reliably on any computing
environment. 
www.techworld-with-nana.com/devops-roadmap


---

## Page 8

When the feature or bugfix is done, a
pipeline running on a CI server (e.g.
Jenkins) should be triggered
automatically, which:
1.runs the tests
2.packages the application
3.builds a container Image
4.pushes the container Image to an
image repository
5.deploys the new version to a
server
CI/CD is kind of the heart of DevOps.
In DevOps, all code changes, like new
features or bug fixes, need to be
integrated in the existing application
and deployed for the end user
continuously and in an automated
way.
Hence the term:
Continuous Integration and
Continuous Deployment (CI/CD)
There are many CI/CD platforms out
there. The most popular one currently
is Jenkins
04
CI/CD Pipelines
Skills you need to learn here:
Setting up the CI/CD server
Integrate code repository to trigger
pipeline automatically
Build & Package Manager Tools to
execute the tests and package the
application
Configuring artifact repositories (like
Nexus) and integrate with pipeline
Configuring deployment to different
environments (cloud, K8s cluster)
Other popular ones: GitLab, GitHub
Actions, Travis CI, Bamboo
www.techworld-with-nana.com/devops-roadmap


---

## Page 9

Nowadays many companies use virtual
infrastructure on the cloud, instead of
managing their own infrastructure. These
are Infrastructure as a Service (IaaS)
platforms, which offer a range of
additional services, like backup, security,
load balancing etc.
These services are platform-specific. So
you need to learn the services of that
specific platform and learn how to
manage the whole deployment
infrastructure on it.
E.g. for AWS you should know the
fundamentals of:
IAM service - managing users and
permissions
VPC service - your private network
EC2 service - virtual servers
AWS is the most powerful and most
widely used IaaS platform, but also a
difficult one.
05
Learn one Cloud Provider
Other popular ones: Microsoft
Azure, Google Cloud
Once you learn one IaaS
platform, it's easy to learn
others
AWS has loads of services, but you only
need to learn the services you/your
company actually needs. E.g. when the
K8s cluster runs on AWS, you need to
learn the EKS service as well.
www.techworld-with-nana.com/devops-roadmap


---

## Page 10

Since containers are popular and easy to
use, many companies are running
hundreds or thousands of containers on
multiple servers. This means these
containers need to be managed
somehow.
For this purpose there are container
orchestration tools.
Kubernetes (also known as K8s) is the
most popular container orchestration
tool
06
Container Orchestration -
Kubernetes
So you need to learn:
How Kubernetes works
How to administer and manage the
K8s cluster
How to deploy applications on K8s
Container orchestration tools like
Kubernetes, automate the deployment,
scaling and management of
containerized applications.
Specific K8s knowledge needed:
Learn core components like,
Deployment, Service, ConfigMap,
Secret, StatefulSet, Ingress
Kubernetes CLI (Kubectl)
Persisting data with K8s Volumes
Namespaces
www.techworld-with-nana.com/devops-roadmap


---

## Page 11

So one of your responsibilities as a
DevOps engineer is to:
setup software monitoring
setup infrastructure monitoring, e.g.
for your Kubernetes cluster and
underlying servers
visualize the data
Once software is in production, it is
important to monitor it to track the
performance, discover problems in your
infrastructure and the application.
Prometheus:
A popular monitoring
and alerting tool
07
Monitoring &
Observability
www.techworld-with-nana.com/devops-roadmap
Grafana:
Analytics and
interactive visualization
tool
ELK Stack:
A popular log
management stack
You should also understand how
systems can collect and aggregate data
with the goal of using it to troubleshoot,
gain business insights etc.


---

## Page 12

Manually creating and maintaining
infrastructure is time consuming and
error prone. Especially when you need
to replicate the infrastructure, e.g. for a
Development, Testing and Production
environment.
In DevOps, we want to automate as
much as possible and that's where
Infrastructure as Code comes into the
picture.
With IaC we use code to create and
configure infrastructure and there are 2
types of IaC tools you need to know:
1.  Infrastructure provisioning
2.  Configuration management
DEV
TEST
PROD
08
Infrastructure as Code
www.techworld-with-nana.com/devops-roadmap
Terraform is the most
popular infrastructure
provisioning tool
Benefits of having everything as code :
Encourage collaboration in a team
Document changes to infrastructure
Transparency of the infrastructure
state
Accessibility to that information in a
centralized place versus being
scattered on people's local machines
in the form of some scripts.
Ansible is the most
popular configuration
management tool


---

## Page 13

Since you are closely working with
developers and system administrators to
also automate tasks for development and
operations, you will need to write scripts
and small applications to automate them.
For that, you will need some scripting or
basic programming skills.
Examples: utility scripts like flushing the
cache, starting the builds and
deployments etc.
09
Scripting Language
www.techworld-with-nana.com/devops-roadmap
Python is one of the most popular
programming languages and easy to
learn
There are many programming languages,
but I would recommend starting with
Python. 
Python is widely used, easy to learn and
used for many different use cases,
especially in DevOps.
And the good thing is, programming
concepts stay the same, so when you
learn one language well, you can easily
learn new ones quite quickly.
You don't need the same level
as a software developer.
Learning how to write scripts
with Python will be enough.
This could be an OS-
specific scripting language
like bash or Powershell.
But what's more demanded is an OS-
independent language like Python, Ruby
or Go.
These languages are more powerful and
flexible. If you know one of these, it will
make you much more valuable as a
DevOps engineer.


---

## Page 14

You write all automation logic as code.
And just application code, automation
code should also be managed and hosted
on a version control tool, like Git.
Infrastructure as Code
K8s config files
Python scripts
10
Version Control - Git
www.techworld-with-nana.com/devops-roadmap
You need to learn Git. It's the most
popular and widely used version
control tool
Do NOT store secrets and
passwords in your Git
repository
Git repository
Git is a CLI Tool, which you install locally.
It enables the tracking of changes in the
source code and enables better
collaboration on code.
Your files are stored centrally in a remote
Git repository on the web. Most popular
Git repositories are GitHub and GitLab.
So you need to learn:
The core Git commands, like git clone,
git branch, git pull/push, git merge etc
But also how to collaborate on a
project, like create pull requests, code
reviews, branching


---

## Page 15

Read their stories and get inspired
or copy link: 
https://www.techworld-with-nana.com/success-stories
This is how learning those skills,
literally changed lives and careers
of our students


---

## Page 16

Software Developer
Starting from..
Having those DevOps skills is the final goal, but many of you start
your DevOps journey having various different backgrounds. 
So the starting point is different for all of you. You may be starting
as a systems administrator or software engineer or test
automation engineer etc or may not have an IT background at all
and want to transition into DevOps:
Systems Administrator
Network Engineer
Test Automation Engineer
www.techworld-with-nana.com/devops-roadmap


---

## Page 17

Some other tasks you might do are things like:
monitoring systems,
health, backup and disaster recovery,
database administration,
network administration or
security administration
So you already have a lot of skills you can use
in the deployment and operations side of
DevOps.
Systems Administrator
Starting as a...
Systems Administrator
You know how to administer servers and other
systems. So you already have some skills in:
setting up infrastructure
configuring and preparing it for deployment
working with operating systems, installing
and running software
security, networking configuration
The big part missing here to start in DevOps is
learning the software development basics:
Understanding the Git workflows
How developers work 
How to create a CI/CD pipeline
www.techworld-with-nana.com/devops-roadmap


---

## Page 18

Software Developer
Starting as a...
Software Developer
If you are a software developer, you have a
pretty good background, because you already
know important parts of DevOps, which are
software development workflows and release
pipelines.
But you are missing skills in server management.
So you need to start by learning about:
Linux, OS basics and virtual machines
creating and configuring servers
configuring infrastructure security,
networking etc.
www.techworld-with-nana.com/devops-roadmap
And since most modern applications run on cloud, you need to learn how to do all
these on a cloud infrastructure.
So that would be your starting point when learning DevOps as a software developer.
And once you have that foundation you can build on that by learning about how
containers work on top of the virtual machines and how to run applications in
containers and how to run containers on a platform like Kubernetes etc.
Your programming skills will also
be great help in writing automated
scripts for various parts of the
application development and
deployment processes.


---

## Page 19

Test Automation Engineer
Starting as a...
Test Automation Engineer
Another common background people have
when transitioning into DevOps is a test
automation engineering.
Here you may have a bit more catching up to do
and more skills to learn compared to developers
or systems administrators, but you can
definitely reuse many of your skills in DevOps.
Like developers, you are missing skills in server management. So
you need to start by learning about:
virtual machines and Linux basics
creating and configuring servers
configuring infrastructure security, networking etc.
www.techworld-with-nana.com/devops-roadmap
You most probably know how the developers work, like the agile processes, Jira
workflows and so on. And as part of your test automation knowledge you understand
the different testing scopes.
You also understand how to test different aspects of an application and that
knowledge is really helpful for setting up an automated CI/CD pipeline, because in
order to automate and streamline delivering your application changes all the way
to the production environment, you need extensive automated testing:


---

## Page 20

Network Engineer
Starting as a...
Network Engineer
Another common background
people have when transitioning
into DevOps is network
engineering. This is probably the
farthest from DevOps compared
to the other three, but you still
have some skills that you can
bring into DevOps as a network
engineer.
So a good starting point for network engineers is to move to cloud
engineering first and then move on to containers and Kubernetes
www.techworld-with-nana.com/devops-roadmap
As a network engineer you know how to configure devices and networking between
devices. So you have valuable knowledge in configuring networking for
infrastructure on premise.
Transition to Cloud Network Engineer
But as most companies are moving their
infrastructure to cloud, many network engineers
transition to cloud network engineering,
configuring virtual routes, switches etc.
With this knowledge you have an advantage to understand networking in
containers and Kubernetes, which is how most modern applications are
running. Networking in containers and K8s is pretty complex, especially
when we need to secure and troubleshoot those networks.
Some network engineers even know scripting in bash or python for example, which
is another helpful skill when it comes to automation part of DevOps.


---

## Page 21

Now this is a very tricky one, because DevOps is NOT an entry-level profession in
IT. It's not the first thing you learn when you want to get into the IT field.
Now why is that?
Non IT Background
Starting with...
No or little IT Background
Some people want to get into DevOps having
very little to no IT background. This means there
are probably some of you reading this, thinking
about getting into DevOps without much IT pre-
knowledge and want to know what the path is to
DevOps.
www.techworld-with-nana.com/devops-roadmap
DevOps is about automating processes in software
development and deployment lifecycle that
people have done manually before.
This means, before you automate processes and tasks that are done manually, you
first need to understand what those processes and tasks are in the first place. If you
don't understand those, you won't know what you're automating or why you even
need DevOps.


---

## Page 22

Go find some example projects, where you create a super simple web application
and learn how to deploy it to a virtual server. In this process you will learn the steps
of developing, packaging, maybe automatically testing and then deploying an
example web application on a Linux server on a cloud platform.
This will teach you the basics of the complete software development lifecycle, but
most importantly it will make you understand each step in the complete workflow
and what goes into that.
Starting with...
No or little IT Background
www.techworld-with-nana.com/devops-roadmap
1 - Understand complete software
development lifecycle
2 - How software development teams collaborate
After that, go ahead and watch some tutorials about agile and
scrum methods and how software development teams
collaborate and work in IT projects.
3 - DevOps Pre-Requisites and 4 - DevOps Skills
These skills will actually be enough to start learning DevOps with our
DevOps Bootcamp for example, because in our bootcamp, you actually
learn Linux, Git and all these basic tools from scratch. 
But again you need to understand those workflows first in order to
understand, why we're using Git, why we need Jenkins, why we're learning
Linux and scripting, we we use containers etc.


---

## Page 23

www.techworld-with-nana.com/devops-roadmap
6 DevOps Career Paths
There's this moment that hits when you realize "DevOps" isn't just
one clear-cut role.
You'll see job listings for Cloud Engineers, SREs, Platform
Engineers, DevOps Engineers – all requiring "DevOps skills".
DevOps serve as the foundation to at least six different high-
growth career paths.
Each with its own focus, challenges, and impressive salary
potential:
4. Site Reliability Engineer
5. DevSecOps Engineer
6. MLOps Engineer
1.DevOps Engineer
2.Cloud Engineer
3.Platform Engineer


---

## Page 24

www.techworld-with-nana.com/devops-roadmap
DevOps Engineer
This is James's story.
After 4 years as a system administrator feeling stuck at $75K, James made the
leap to DevOps.
Now he spends his days building CI/CD pipelines, managing Kubernetes clusters,
and automating infrastructure with Terraform.
He loves that his work directly impacts how quickly new features reach
customers.
"I'm the bridge between developers and operations," he told me recently. "When
either team has a bottleneck, I'm the one who gets to solve it."
Cloud Architect
Miguel's transformation still amazes me.
He was a traditional IT manager overseeing on-premise infrastructure when
cloud adoption started leaving him behind.
After mastering DevOps principles and cloud platforms, he now designs multi-
region architectures that scale automatically with demand.
He's the go-to person for making critical decisions about cloud services,
security, and cost optimization.
"I basically build digital cities in the cloud," he explains. "Planning the streets,
utilities, and safety systems so everything works together."
Most direct path!
Focus: Cloud platform expertise and architecture design


---

## Page 25

www.techworld-with-nana.com/devops-roadmap
Site Reliability Engineer
Meet Priya.
She was a QA engineer who found herself drawn to the reliability side of DevOps
during our program.
Now as an SRE at a fintech company, she's obsessed with uptime, performance
metrics, and building systems that gracefully handle failure.
Her team gets paged less than any other because they've built resilience into
everything.
"I love the high stakes," she says. "When millions of dollars in transactions flow
through systems you're responsible for, you learn to build things right the first
time."
Platform Engineer
Lisa found her perfect fit here.
With a background in both development and IT operations, she now builds
internal developer platforms that make other engineers more productive.
"I create the systems that let developers focus on code instead of
infrastructure," she explains. "It's like I'm building a product, but my users are
other engineers."
Her platforms have cut deployment times from days to minutes and significantly
improved developer satisfaction scores.
Focus: System reliability, performance, and incident management
Focus: Internal developer platforms and tool creation


---

## Page 26

www.techworld-with-nana.com/devops-roadmap
DevSecOps Specialist
Then there's Omar.
He combined his security background with DevOps practices to become his
company's security champion.
Now he ensures security is built into every stage of the development pipeline
rather than tacked on at the end.
He automates security scanning, manages vulnerability response, and trains
teams on secure coding practices.
"In a world of increasing cyber threats, I help companies ship code faster
without creating new vulnerabilities," he says.
MLOps Engineer
This is David's journey.
After 3 years as a software engineer feeling disconnected from the AI revolution, 
David made the switch to MLOps.
Now he spends his days building ML pipelines, managing model deployments,
and creating the infrastructure that turns experimental notebooks into
production systems.
He loves that his work is the bridge between data science research and real-
world impact:
"I take the models that data scientists create and make them work for millions of
users. When a recommendation system helps someone discover their new
favorite product, I built the pipeline that made it possible."
Focus: Takes DevOps skills and applies them specifically to
machine learning workflows.
Focus: Security integration throughout development lifecycle.


---

## Page 27

www.techworld-with-nana.com/devops-roadmap
Cloud Engineer/Architect
Cloud Engineer vs DevOps Engineer
Cloud Engineer Roadmap
Platform Engineer
What is Platform Engineering and how
it fits into DevOps and Cloud
SRE
What is SRE and how it
compares to DevOps
DevSecOps Engineer
What is DevSecOps
MLOps Engineer
What is MLOps
Learn more about
each Roles
DevOps Engineer
I Analyzed 100+ Job Posts


---

## Page 28

Summary
DevOps Roadmap
www.techworld-with-nana.com/devops-roadmap
1 - Getting the prerequisites right
So as a system administrator or a network engineer, learn the
software development workflows. As a developer, learn the
basics of infrastructure, virtual servers etc.
Of course with zero IT background, you have to get all this
prerequisite knowledge from server administration to
development first. So you have a more difficult entry, but it is
possible if you know what to learn.
First step is to get the DevOps prerequisites right. So depending on which background and pre-
knowledge you have, you need to first make sure to get any missing prerequisite knowledge.
2 - Cloud, Docker, K8s
After learning the prerequisites, you can
already get started with important DevOps
skills of working with containers and container
orchestration tools. So basically learning
Docker and Kubernetes to help your teams
deploy and efficiently run the application.
And since most of the modern applications and
Kubernetes clusters are running on cloud, you
need to learn cloud infrastructure, how to work
with cloud infrastructure, how to configure it,
how to scale it and so on.
3 - Automation
As a DevOps professional automation skills are
one of the most important ones. And as the
heart of DevOps, learning to build CI/CD
pipelines is an essential skill.
Finally you will learn how to automate parts of
the complete DevOps processes one by one
using the concepts and tools of what's called X
as code: IaC, Configuration as Code, Security
as Code, Policy as Code and so on, which
basically means just automating everything in
the form of code!
4 - Go from there. Keep learning
DevOps is evolving and new tools are being developed all the time. So as a DevOps professional,
you should learn how to evaluate and test many new tools, always with the same goal to optimize
and automate existing processes and make them more efficient.


---

## Page 29

DevOps and Cloud engineering is
extremely rewarding but also very
challenging to learn  Resources for your
DevOps & Cloud Career
In just 6-months, you’ll be able to build complex
DevOps processes with confidence
or copy link: 
https://www.techworld-with-nana.com/devops-bootcamp
That’s why our Bootcamps give you a meticulously structured
learning guide to make learning these challenging professions
as simple as possible!
Take Action Today


---

