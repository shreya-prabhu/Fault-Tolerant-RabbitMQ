# Reliable Messaging Solution with High Availability using Rabbit MQ
To implement fault tolerance in the distributed system.

### Features
 - An active standby server which takes the place of the main server whan it has crashed
 - All messages before the crash also sent to the passive server, so no data is lost
 - once main server is crashed, clients  messages are sent  to passive server automatically
 - whenever a new client joins and active server is not available, new client is also registered to send messages
   to passive server

### Installation
- ```chmod +x configure```
- To configure server  
  ```sudo ./configure -s```
- To configure client  
  ```sudo ./configure -c```
### Set Up
To change hostname of active and passive machines
```
sudo hostnamectl set-hostname active
sudo hostnamectl set-hostname passive
```

edit /etc/hosts file on other machines and append    
<IP_active>  active    
<IP_passive>  passive    

