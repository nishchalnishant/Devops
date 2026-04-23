# Content from CheatSheet_Linux.pdf

## Page 1

Command
Description
*
Wildcard symbol for variable length, e.g., *.txt
refers to all files with the TXT extension
?
Wildcard symbol referring to a single
character, e.g., Doc?.docx can refer to
Doc1.docx, DocA.docx, etc. 
ls
List the names of files and subfolders the
current directory. Options include -l, - a, -t
which you may combine, e.g., -alt.
ls -l
Also show details of each item displayed, such
as user permissions and the time/date when the
item was last modified
ls -a
Also display hidden files/folders. May combined
with ls -l to form ls -al. 
ls -t
Sort the files/folders according to the last
modified time/date, starting with the most
recently modified item
cd
To the $HOME directory
cd ..
Up one level to enclosing folder or parent
directory
cd /etc
To the /etc directory
cmp A B
Compare two files A and B for samenes No
output if A and B are identical, outputs
character and line number otherwise.
Shubham
TrainWith
Shubham
TrainWith
Linux-Cheatsheet
Cheatsheet for DevOps Engineers
This cheatsheet covers essential Linux commands required in the daily life of a
DevOps Engineer, categorized for easy reference.
File Management:


---

## Page 2

Shubham
TrainWith
Command
Description
diff A B 
Compare two files A and B for differ Outputs
the difference.
pwd
Display the path of the current working
directory.
mkdir X
Make a new directory named X inside the
current directory.
mv A B
Move a file from path A to path B. Al used for
renaming files.Examples:- Movi between
directories folder1 and folder2:
‘mv ./folder1/file.txt ./folder2’
The file name will remain unchanged, and i new
path will be ./folder2/file.txt Renaming a file:
mv new_doc.t expenses.txt. The new file name
expenses.txt.
cp A B
Copy a file from path A to path B. Usa similar
to mv both in moving to a new directory and
simultaneously renaming the file in its new
location.
Example: ./f1/file.txt ./f2/expenses.txt
simultaneous copies the file file.txt to the new
location with a new name expenses.txt
cp -r Y Z 
Recursively copy a directory Y and its contents
to Z. If Z exists, copy source Y into it;
otherwise, create Z and Y becomes its
subdirectory with Y’s contents
rm X
Remove (delete) X permanently.
rm -r Y
Recursively delete a directory Y and its
contents
rm -f X
Forcibly remove file X without prompts
confirmation
rm -rf Y
Forcibly remove directory Y and its contents
recursively
rmdir Y
Remove a directory Y permanently, provided Y
is empty.
Shubham
TrainWith
Shubham
ainWith


---

## Page 3

Shubham
TrainWith
Command
Description
open X
Open X in its default program. 
open -e X
Opens X in the default text editor (macOS:
TextEdit)
touch X
Create an empty file X or update the access
and modification times of X.
cat X
View contents of X.
cat -b X
Also display line numbers as well.
wc X
Display word count of X.
head X
Display the first 10 lines of X. If more th a
single file is specified, each f preceded by a
header consisting of the string "==> X <==''
where "X'' is the name of the file.
head -n 4 X
Show the first 4 lines of X.
tail X
Display the last (10, by default) lines of X. Ife
more than a single file is specified, each file is
preceded by a header consisting of the string
"==> X <=='' where "X'' is the name of the file.
tail -n +1 X
Display entire contents of the file(s) X
specified, with header of respective file name.
tail -f X
Display the last 10 lines of the file(s) X
specified, and track changes appended to them
at the end. Overwriting X or modifying X with a
text editor such as vim would mess up this
command’s output.
less
Read a file with forward and backward
navigation. Often used with pipe, 
e.g., cat file.txt
ln -s A S
Create symbolic link of path A to link name S
Shubham
TrainWith
Shubham
TrainWith


---

## Page 4

Shubham
TrainWith
Command
Description
echo TEXT 
Display a line of TEXT or the contents of a
variable.
open -e TEXT
Also interprets escape characters in TEXT,
e.g., \\n → new line, \\b → backslash, \\t →
tab.
echo -n TEXT
Omits trailing newline of TEXT
cmd > file
Redirect output of a command cmd to a file.
Overwrites pre-existing content of file.
cmd >& file
Redirect output of cmd to file. Overwrites pre-
existing content of file. Suppresses the output
of cmd.
cmd > /dev/null
Suppress the output of cmd.
cmd >> file
Append output of cmd to file
cmd < file
Read input of cmd from file.
cmd << delim
Read input of cmd from the standard input with
the delimiter character delim to tell the system
where to terminate the input. Example for
counting the number of lines of ad-hoc input:wc
-l << EOF> I like> apples> and> oranges.> EOF 4
Hence there are only 4 lines in the standard
input delimited by EOF.
cmd <<< string
Input a text string to cmd.
cmd 2> foo
Redirect error messages of cmd to foo.
cmd 2>> foo
Append error messages of cmd to foo
cmd &> file
Redirect output and error messages of cmd to
file
Shubham
TrainWith
Input/Output Redirection: 
Shubham
TrainWith


---

## Page 5

Shubham
TrainWith
Command
Description
grep patt /path/to/src
Search for a text pattern patt in X. Commonly
used with pipe e.g., `ps aux
grep -r patt /path/to/src
Search recursively (the target directory
/path/to/src and its subdirectories) for a text
pattern patt.
grep -v patt X 
Return lines in X not matching the specified
patt.
grep -l patt X
Write to standard output the names of files
containing patt.
grep -i patt X 
Perform case-insensitive matching on X. Ignore
the case of patt.
find
find files
find /path/to/src -name "*.sh"
Find all files in /path/to/src matching the
pattern "*.sh" in the file name
find /home -size +100M 
Find all files in the /home directory larger than
100MB.
locate name
Find files and directories by name.
sort X
Arrange lines of text in X alphabetically or
numerically.
Shubham
TrainWith
Search and Filter:
Shubham
TrainWith


---

## Page 6

Shubham
TrainWith
Command
Description
tar
Manipulate archives with .tar extension.
tar -v
Get verbose output while manipulating TAR
archives. May combine this option with others,
e.g., tar -tvf.
tar -cf archive.tar Y
Create a TAR archive named archive.tar
containing Y.
tar -xf archive.tar
Extract the TAR archive named archive.tar.
tar -tf archive.tar
List contents of the TAR archive named
archive.tar.
tar -czf archive.tar.gz Y 
Create a gzip-compressed TAR archive named
archive.tar.gz containing Y.
tar -xzf archive.tar.gz
Extract the gzip-compressed TAR archive
named archive.tar.gz.
tar -cjf archiave.tar.bz2 Y
Create a bzip2-compressed TAR archive named
archive.tar.bz2 containing Y.
tar -xjf archive.tar.bz2
Extract the bzip2-compressed TAR archive
named archive.tar.bz2.
gzip
Manipulate archives with .gz extension.
gzip Y
Create a gzip archive named Y.gz containing Y.
gzip -l Y.gz
List contents of gzip archive Y.gz. 
gzip -d Y.gzgunzip Y.gz
Extract Y.gz and recover the original file Y
bzip2
Manipulate archives with .bz2 extension.
Shubham
TrainWith
Archives:
Shubham
TrainWith


---

## Page 7

Command
Description
bzip2 Y
Create a bzip2 archive named Y.bz2 containing
Y.
bzip2 -d Y.gzbunzip2 Y.gz
Extract Y.bz2 and recover the original file Y.
zip -r Z.zip Y
Zip Y to the ZIP archive Z.zip.
unzip Z.zip
Unzip Z.zip to the current directory
unzip Z.zip
List contents of Z.zip
File Transfer:
Command
Description
ssh user@access
Connect to access as user.
ssh access
Connect to access as your local username.
ssh -p port user@access
Connect to access as user using port.
scp [user1@]host1:[path1] [user2@]host2:[path2]
Login to hostN as userN via secure copy
protocol for N=1,2.Example usage:scp
alice@pi:/home/source
bob@arduino:/destinationpath1 and
path2 may be local or remote, but ensure
they’re absolute rather than relative
paths, e.g., /var/www/*.html, /usr/bin.If
user1 and user2 are not specified, scp will
use your local username.
scp -P port [user1@]host1:[path1] [user2@]host2:
[path2] 
Connect to hostN as userN using port for
N=1,2.
scp -r [user1@]host1:[path1] [user2@]host2:
[path2] 
Recursively copy all files and directori
from path1 to path2. 
sftp [user@]access
Login to access as user via secure file
transfer protocol. If user is not
specified your local username will be
used.
Shubham
TrainWith
Shubham
TrainWith


---

## Page 8

Command
Description
sftp access
Connect to access as your local username. 
sftp -P port user@access
Connect to access as user using port.
rsync -a [path1] [path2]
Synchronize [path1] to [path2], preserving
symbolic links, attributes, permissions,
ownerships, and other settings. 
rsync -avz host1:[path1] [path2] 
Synchronize [path1] on the remote host host1
to the local path [path2], preserving symbolic
links, attributes, permissions, ownerships, and
other settings. It also compress the data
during the transfer.
Shubham
TrainWith
File Permissions:
Command
Description
chmod permission file
Change permissions of a file or directory.
Permissions may be of the form [u/g/o/a]
[+/-/=][r/w/x] (see examples below) or a three-
digit octal number.
chown user2 file 
Change the owner of a file to user2
chgrp group2 file
Change the group of a file to group2
Usage examples:
chmod +x testfile → allow all users to execute the file
chmod u-w testfile → forbid the current user from writing or changing the file
chmod u+wx,g-x,o=rx testfile → simultaneously add write and execute
permissions to use remove execute permission from group, and set the
permissions of other users to only read and write
Shubham
TrainWith


---

## Page 9

Numeric Representation:
The table below compares Linux file permissions in octal form and in the format
[u/g/o/ [+/-/=][r/w/x].
Octal
Permission(s)
Equivalent to application of
0
No permissions
-rwx
1
Execute permission only 
=x
2
Write permission only
=w
3
Write and execute
permissions only: 2 + 1 = 3
=wx
4
Read permission only
=r
5
Read and execute permissions
only: 4 + 1 = 5 
=rx
6
Read and write permissions
only: 4 + 2 = 6
=rw
7
All permissions: 4 + 2 + 1 = 7 
=rwx
Shubham
TrainWith
Examples:
chmod 777 testfile → allow all users to execute the file
chmod 177 testfile → restrict current user (u) to execute-only, while the
group (g) and other users (o) have read, write and execute permissions
chmod 365 testfile → user (u) gets to write and execute only; group (g), read
and write only; others (o), read and execute only.
Shubham
TrainWith


---

## Page 10

System Information:
Command
Description
uname
Show the Linux system information.
uname -a 
Detailed Linux system information
uname -r
Kernel release information, such as kernel
version
uptime
Show how long the system is running and load
information.
su sudo
Superuser; use this before a command that
requires root access e.g., su shutdown 
cal
Show calendar where the current date is
highlighted.
date
Show the current date and time of the
machine.
halt
Stop the system immediately.
shutdown
Shut down the system.
reboot
Restart the system.
last reboot 
Show reboot history.
man COMMAND 
Shows the manual for a given COMMAND. To
exit the manual, press “q”.
hostname
Show system host name
hostname -I 
Display IP address of host
cat /etc/*-release 
Show the version of the Linux distribution
installed. For example, if you’re using Red Hat
Linux, you may replace * with redhat.
Shubham
TrainWith
Shubham
TrainWith


---

## Page 11

Hardware:
Command
Description
dmesg
Display messages in kernel ring buffer (data
structure that records messages related to
the operation of the program running the
operating system)
cat /proc/cpuinfo 
Display information about the central
processing unit (CPU)
cat /proc/meminfo
Display memory information
lspci -tv 
Displays information about each Peripheral
Component Interconnect (PCI) device on your
system.The option -t outputs the information
as a tree diagram, and -v is for verbose output.
lsusb -tv
Display information about Universal Serial Bus
(USB) devices and the devices connected to
them.The option -t outputs the information as
a tree diagram, and -v is for verbose output.
dmidecode
Display system hardware components, serial
numbers, and BIOS version
hdparm -i /dev/sda
Display information about the disk sda
hdparm -tT /dev/sda
Perform a read speed test on the disk sda
badblocks -s /dev/sda
Test for unreadable blocks on the disk sda 
Shubham
TrainWith
Shubham
TrainWith


---

## Page 12

Disk Usage: 
Command
Description
df
Display free disk space.
du
Show file/folder sizes on disk
du -ah 
Disk usage in human readable format (KB, MB
etc.) 
du -sh
Total disk usage of the current directory
du -h 
Free and used space on mounted filesystems
du -i
Free and used inodes on mounted filesystems
fdisk -l 
List disk partitions, sizes, and types
free -h
Display free and used memory in human
readable units.
free -m
Display free and used memory in MB.
free -g
Display free and used memory in GB. 
Shubham
TrainWith
Process Management and Performance Monitoring: 
Command
Description
&
Add this character to the end of a
command/process to run it in the background
ps
Show process status. Often used with grep
e.g., `ps aux
ps -eps -A
Either of these two commands prints all
running processes in the system
ps -ef
Print detailed overview
ps -U root -u root
Display all processes running under the
account root. 
Shubham
TrainWith


---

## Page 13

Command
Description
ps -eo pid,user,command 
Display only the columns pid, user and
command in ps output
top
Display sorted information about processes
htop
Display sorted information about processes
with visual highlights. It allows you to scroll
vertically and horizontally, so you can see
every process running on your system and
entire commands.
atop
Display detailed information about processes
and hardware
kill PID
Kill a process specified by its process ID PID,
which you obtain using the ps command
killall proc1 
Kill all processes containing proc1 in their
namess
lsof
List all open files on the system. (This
command helps you pinpoint what files and
processes are preventing you from
successfully ejecting an external drive.) 
lsof -u root 
List all files on the system opened by the root
user. As the output can be long, you may use
`lsof -u root
mpstat 1
Display processor-related statistics, updated
every second (hence the 1, whereas mpstat 2
refreshes the output every 2 seconds)
vmstat 1
Display virtual memory statistics (information
about memory, system processes, paging,
interrupts, block I/O, disk, and CPU
scheduling), updated every (1) second
iostat 1
Display system input/output statistics for
devices and partitions. virtual memory
statistics, updated every (1) second 
tail -n 100 /var/log/messages
Display the last 100 lines in the system
logs.Replace /var/log/messages with
/var/log/syslog for Debian-based systems. 
Shubham
TrainWith
Shubham
TrainWith


---

## Page 14

Command
Description
tcpdump -i eth0 
Capture and display all packets on interface
eth0
tcpdump -i eth0 port 80
Monitor all traffic on interface eth0 port 80
(HTTP)
watch df -h
Execute df -h and show periodic updates, To
exit, press Ctrl+C
User Management:
Command
Description
who
Display who is logged in
w
Display what users are online and what they
are doing
users
List current users
whoami
Display what user you are logged in as
id
Display the user ID and group IDs of your
current user 
last
Display the last users who have logged onto
the system
groupadd gp1
Create a group named gp1
useradd -c "Alice Bob" -m ab1
Create an account named ab1, with a comment
of "Alice Bob" and create the new user’s home
directory 
userdel ab1
Delete the account named ab1
usermod -aG gp1 ab1
Add the account ab1 to the group gp1 
Shubham
TrainWith
Shubham
TrainWith


---

## Page 15

Networking:
Command
Description
ifconfig
Display all network interfaces with IP
addresses
ifconfig -a
Display all network interfaces, even if any of
them is down, with IP addresses
ifconfig eth0
Display IP addresses and details of the eth0
interface
ip a
Another way to display all network interfaces
with IP addresses 
ethtool eth0 
Query or control network driver and hardware
settings of the interface eth0 
netstat
Print open sockets of network connections,
routing tables, interface statistics,
masquerade connections, and multicast
memberships.Pipe with the less command: e.g.,
`netstat -a
netstat -a
Show both listening and non-listening sockets
netstat -l
Show only listening sockets
netstat -nutlp
Show listening TCP and UDP ports and
corresponding programs 
ping host
Send ICMP echo request to host, which may be
a symbolic name, domain name or IP address
whois domain
Display whois information for domain 
dig domain
Display DNS information for domain 
dig -x addr
Do a reverse lookup on an IPv4 or IPv6
address addr 
host domain 
Display DNS IP address for domain 
wget LINK
Download from location LINK
Shubham
TrainWith
Shubham
TrainWith


---

## Page 16

Command
Description
curl LINK
Display the HTML source of LINK. 
ufw allow port 
Allow traffic on a specific port through the
firewall.
ufw status
Check the status of the Uncomplicated
Firewall.
nmcli
Command-line tool for managing network
connections
Shubham
TrainWith
Package Management Commands: 
Linux Distribution
Debian/Ubuntu
Rocky / Fedora /
Red Hat Enterprise
Linux
Arch Linux /
Manjaro / Garuda /
Chakra 
Update list of
packages available
from remote
repositories
sudo apt update
dnf check-update
The command pacman
-Syy achieves this
purpose but may
damage your
system.Use pacman -
Syu instead. 
Upgrade installed
packages
sudo apt upgrade
sudo dnf upgrade 
pacman -Syu
Find a package with
keyword in the name
apt search keyword 
dnf search keyword
pacman -Ss keyword
View description and
summary information
about a package
apt show package 
dnf info package
pacman -Si package
Install a package
(with appropriate file
extension) the local
file system
sudo dpkg -i
package.deb
sudo dnf install
package.rpm
pacman -S package
Remove / uninstall a
package
sudo apt remove
package
sudo dnf erase
package
pacman -R package
Shubham
TrainWith


---

