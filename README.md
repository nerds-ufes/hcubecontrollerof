HCube Openflow Controller
========================


Description
---
OpenFlow controller for networks complete and incomplete Hypercube.

Instalation
---

```sh
$ sudo pip install ryu
$ sudo pip install networkx
$ sudo pip install colorama
```

Starting the tests
-----

**Running the controller**

```sh
$ cd hcubecontrollerof/
$ ryu-manager --observe-links hcubecontrollerof.hcubecontrollerof
```

**Starting mininet**

```sh
$ cd hcubecontrollerof/tests/
$ sudo python mn_hypercube_topology.py
```

Developers
---
 
* Rafael Silva Guimarães <rafaelg@ifes.edu.br>
* Dione Souza Albuquerque de Lima <dione.souza@gmail.com>
	
