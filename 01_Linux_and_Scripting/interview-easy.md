## Easy

**1. What is the difference between a process and a thread?**
A process is an independent program with its own memory space. A thread is a lighter unit of execution within a process that shares the same memory space with other threads in that process.

**2. What does `chmod 755` do?**
It sets permissions so the owner has read, write, and execute (7), and group and others have read and execute (5).

**3. What is the difference between `>` and `>>` in shell?**
`>` redirects output to a file and overwrites it. `>>` appends output to the end of the file.

**4. How do you find all files larger than 100MB in Linux?**
```bash
find / -type f -size +100M
```

**5. What is a symbolic link vs a hard link?**
A hard link points directly to the same inode (data blocks). A symbolic link points to a path. Deleting the original file breaks a symlink but not a hard link.

**6. What does `ps aux` show?**
It lists all running processes for all users with CPU, memory, PID, command, and state information.

**7. How do you check disk usage per directory?**
```bash
du -sh /path/to/dir
```

**8. What is `ulimit` used for?**
`ulimit` sets per-process resource limits such as maximum open files, stack size, and maximum memory.

**9. What is the difference between `kill` and `kill -9`?**
`kill` sends SIGTERM (15) which allows the process to clean up. `kill -9` sends SIGKILL which the kernel terminates immediately with no cleanup.

**10. How do you check which port a process is listening on?**
```bash
ss -tlnp
# or
netstat -tlnp
```

**11. What is the sticky bit?**
A permission flag on directories that allows only the file owner to delete or rename their own files within the directory. Used on `/tmp`.

**12. What does `/etc/fstab` do?**
It defines filesystems and their mount options that are automatically mounted at boot.

**13. What is a cron job?**
A cron job is a scheduled task defined in a crontab that the cron daemon runs at specified intervals.

**14. How do you view running services in systemd?**
```bash
systemctl list-units --type=service --state=running
```

**15. What is the purpose of `/proc`?**
`/proc` is a virtual filesystem exposing kernel and process information as files. `/proc/cpuinfo`, `/proc/meminfo`, `/proc/PID/` are common examples.

**16. What does `awk` do?**
`awk` is a text processing tool that reads line by line, splits fields by delimiter, and applies expressions. Used for data extraction and transformation.

**17. What is `sed` used for?**
`sed` is a stream editor for filtering and transforming text — find/replace, deletion, insertion — without opening the file.

**18. What is `xargs`?**
`xargs` reads items from stdin and passes them as arguments to another command. Example: `find . -name "*.log" | xargs rm`.

**19. What is the difference between `source` and executing a script?**
`source script.sh` runs the script in the current shell, so variable assignments persist. Executing `./script.sh` runs it in a subshell — changes don't affect the parent.

**20. How do you create a new directory?**
`mkdir directory_name`

**21. How do you delete a non-empty directory?**
`rm -rf directory_name`

**22. How do you rename a file?**
`mv old_name new_name`

**23. How do you copy a file?**
`cp source_file destination_file`

**24. How do you see the last 10 lines of a file?**
`tail filename`

**25. How do you see the first 10 lines of a file?**
`head filename`

**26. How do you search for a word in a file?**
`grep "word" filename`

**27. How do you clear the terminal screen?**
`clear` or `Ctrl+L`

**28. How do you see the history of commands you typed?**
`history`

**29. How do you create a new empty file?**
`touch filename`

**30. How do you change your password?**
`passwd`

**31. How do you exit from the terminal?**
`exit` or `logout` or `Ctrl+D`

**32. How do you list all files including hidden ones?**
`ls -a`

**33. How do you print text to the terminal?**
`echo "hello world"`

**34. What command tells you which directory you are currently in?**
`pwd` (Print Working Directory)
