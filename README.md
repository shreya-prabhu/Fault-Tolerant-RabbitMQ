# High-Availability-RabbitMQ
To achieve high availability of the distributed system.

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

