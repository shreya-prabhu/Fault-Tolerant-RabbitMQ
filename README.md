# High-Availability-RabbitMQ
To achieve high availability of the distributed system.

### Installation
Run a shell script with relevant instructions specified in installation.txt

### Set Up
To change hostname of active and passive machines  
Use sudo hostnamectl set-hostname active  
Use sudo hostnamectl set-hostname passive  

edit /etc/hosts file on other machines and append  
<IP_active>  active  
<IP_passive>  passive  

