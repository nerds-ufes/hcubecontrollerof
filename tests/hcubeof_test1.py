#!/usr/bin/env python

from mininet.cli import CLI
from mininet.link import Link
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
import time 

if '__main__' == __name__:

    IP_CONTROLLER = '192.168.52.100'

    net = Mininet(controller=lambda name: RemoteController( name,
                                                            ip=IP_CONTROLLER,
                                                            switch=OVSSwitch ))

    c0 = net.addController('c0')

    #             s5 ......... s6 
    #           . .           . . 
    #         .   .         .   .
    #       s1 ......... s2     . 
    #        .    .      .      .
    #        .    s7 .......... s8 
    #        .   .       .     .
    #        . .         .  .
    #       s3 ......... s4 

    s1 = net.addSwitch('s1',
                       listenPort=6634,
                       protocols='OpenFlow13')
    s2 = net.addSwitch('s2',
                       listenPort=6635,
                       protocols='OpenFlow13')
    s3 = net.addSwitch('s3',
                       listenPort=6636,
                       protocols='OpenFlow13')
    s4 = net.addSwitch('s4',
                       listenPort=6637,
                       protocols='OpenFlow13')
    s5 = net.addSwitch('s5',
                       listenPort=6638,
                       protocols='OpenFlow13')
    s6 = net.addSwitch('s6',
                       listenPort=6639,
                       protocols='OpenFlow13')
    s7 = net.addSwitch('s7',
                       listenPort=6640,
                       protocols='OpenFlow13')
    s8 = net.addSwitch('s8',
                       listenPort=6641,
                       protocols='OpenFlow13')

    h1 = net.addHost(
        'h1', 
        ip="10.0.0.1/24",
        mac='00:00:00:00:00:01'
    )
    h1.cmd('sysctl -p')

    h2 = net.addHost(
        'h2',
        ip="10.0.0.2/24",
        mac="00:00:00:01:00:01"
    )
    h2.cmd('sysctl -p')

    h3 = net.addHost(
        'h3',
        ip="10.0.0.3/24",
        mac="00:00:00:02:00:01"
    )
    h3.cmd('sysctl -p')

    h4 = net.addHost(
        'h4',
        ip="10.0.0.4/24",
        mac="00:00:00:03:00:01"
    )
    h4.cmd('sysctl -p')

    h5 = net.addHost(
        'h5',
        ip="10.0.0.5/24",
        mac="00:00:00:04:00:01"
    )
    h5.cmd('sysctl -p')

    h6 = net.addHost(
        'h6',
        ip="10.0.0.6/24",
        mac="00:00:00:05:00:01"
    )
    h6.cmd('sysctl -p')

    h7 = net.addHost(
        'h7',
        ip="10.0.0.7/24",
        mac="00:00:00:06:00:01"
    )
    h7.cmd('sysctl -p')

    h8 = net.addHost(
        'h8',
        ip="10.0.0.8/24",
        mac="00:00:00:07:00:01"
    )
    h8.cmd('sysctl -p')

    Link(s1, h1)
    Link(s2, h2)
    Link(s3, h3)
    Link(s4, h4)
    Link(s5, h5)
    Link(s6, h6)
    Link(s7, h7)
    Link(s8, h8)

    Link(s1, s2)
    Link(s1, s3)
    Link(s1, s5)
    Link(s2, s4)
    Link(s2, s6)
    Link(s3, s4)
    Link(s3, s7)
    Link(s4, s8)
    Link(s5, s6)
    Link(s5, s7)
    Link(s6, s8)
    Link(s7, s8)
    
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    s5.start([c0])
    s6.start([c0])
    s7.start([c0])
    s8.start([c0])

    time.sleep(4)
    net.pingAll()
    
    #CLI(net)
    time.sleep(4)
    net.pingAll()
    IPERFPATH = '/usr/local/bin/iperf3'
    start_time = time.time()
    # Servidores
    h1.cmd( IPERFPATH + '  -s -1 > h1.txt &')
    h2.cmd( IPERFPATH + '  -s -1 > h2.txt &')
    h3.cmd( IPERFPATH + '  -s -1 > h3.txt &')
    h4.cmd( IPERFPATH + '  -s -1 > h4.txt &')
    h5.cmd( IPERFPATH + '  -s -1 > h5.txt &')
    h6.cmd( IPERFPATH + '  -s -1 > h6.txt &')
    h7.cmd( IPERFPATH + '  -s -1 > h7.txt &')
    h8.cmd( IPERFPATH + '  -s -1 > h8.txt &')
    time.sleep(2)
 
    h8.cmd( IPERFPATH + ' -c '+h1.IP()+'  -u -t 60 -b 30m > h8h1.txt &')
    h2.cmd( IPERFPATH + ' -c '+h5.IP()+'  -u -t 60 -b 30m > h2h5.txt &')
    h5.cmd( IPERFPATH + ' -c '+h8.IP()+'  -u -t 60 -b 30m > h5h8.txt &')
    h1.cmd( IPERFPATH + ' -c '+h7.IP()+'  -u -t 60 -b 30m > h1h7.txt &')
    h3.cmd( IPERFPATH + ' -c '+h6.IP()+'  -u -t 60 -b 30m > h3h6.txt &')
  
    time.sleep(10)
    net.configLinkStatus('s1','s2','down')
    time.sleep(10)
    #net.configLinkStatus('s5','s6','down')
    time.sleep(20)
    net.configLinkStatus('s1','s2','up')
    time.sleep(10)
    #net.configLinkStatus('s5','s6','up')
    time.sleep(10)
    elapsed_time = time.time() - start_time
    print "Elapsed time time: "+str(elapsed_time)
    net.stop()
