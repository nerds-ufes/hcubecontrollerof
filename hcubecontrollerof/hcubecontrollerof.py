# coding: utf-8
__author__ = 'Rafael Silva Guimarães e Dione Sousa Albuquerque'

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib import dpid as dpid_lib
from ryu.lib.packet import vlan
from ryu.ofproto import ether
from ryu.topology import switches, event
import netaddr
import thread
import time
from colorama import Fore
from hypercube import Hypercube

ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__


class HCubeControllerOF(app_manager.RyuApp):

	_CONTEXTS = {
		'switches': switches.Switches,
	}

	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(HCubeControllerOF, self).__init__(*args, **kwargs)
		self.switches = kwargs['switches']
		self.wait = True
		self.newnodefound = False
		self.hypercube = None
		self.mac_to_port = {}
		self.arp_table = {
			'10.0.0.1':'00:00:00:00:00:01',
			'10.0.0.2':'00:00:00:01:00:01',
			'10.0.0.3':'00:00:00:02:00:01',
			'10.0.0.4':'00:00:00:03:00:01',
			'10.0.0.5':'00:00:00:04:00:01',
			'10.0.0.6':'00:00:00:05:00:01',
			'10.0.0.7':'00:00:00:06:00:01',
			'10.0.0.8':'00:00:00:07:00:01'
		}
		self.sw = {}
		self.nodes_restore = []
		thread.start_new_thread(self._generateHypercube)

	def _generateHypercube(self):
		time.sleep(5)
		self.hypercube = Hypercube(3, self.switches, allnodes=True)

		self.wait = False
		for n in self.hypercube.nodes.itervalues():
			self.logger.info("[Generate Hypercube] dpid=[%s], host=[%s], name=[%s], mac=[%s]" %
			                 (n.dpid, n.host, n.binaddr, n.mac))
			for (dpid, port) in n.neighbors.items():
				self.logger.info("[Generate Hypercube] neighbors=[%s] --> (%d  %s)" %
				                 (dpid, port.port_no, port.name))
		self.hypercube.printroute()
		self.logger.info('##################################')

	def _get_mac_from_database(self, ip):
		# Retorna o MAC do host especificado
		mac_hosts = {
		'10.0.0.1':'00:00:00:00:00:01',
		'10.0.0.2':'00:00:00:01:00:01',
		'10.0.0.3':'00:00:00:02:00:01',
		'10.0.0.4':'00:00:00:03:00:01',
		'10.0.0.5':'00:00:00:04:00:01',
		'10.0.0.6':'00:00:00:05:00:01',
		'10.0.0.7':'00:00:00:06:00:01',
		'10.0.0.8':'00:00:00:07:00:01'
		}
		try:
			return mac_hosts[ip]
		except:
			return None

	def _build_ether(self, ethertype, src_mac, dst_mac):
		# Construir o header Ethernet
		e = ethernet.ethernet(dst_mac, src_mac, ethertype)
		return e

	def _build_arp(self, opcode, src_ip, dst_ip, vid=None):
		# Construir o ARP
		if opcode == arp.ARP_REQUEST:
			_eth_dst_mac = self.BROADCAST_MAC
			_arp_dst_mac = self.ZERO_MAC
		elif opcode == arp.ARP_REPLY:
			_eth_dst_mac = self._get_mac_from_database(dst_ip)
			_eth_src_mac = self._get_mac_from_database(src_ip)

		if _eth_dst_mac is None or _eth_src_mac is None:
			return None

		if vid is None:
			e = self._build_ether(ether.ETH_TYPE_ARP, _eth_src_mac, _eth_dst_mac)
			a = arp.arp(
				hwtype=1,
				proto=ether.ETH_TYPE_IP,
				hlen=6,
				plen=4,
				opcode=opcode,
				src_mac=_eth_src_mac,
				src_ip=src_ip,
				dst_mac=_eth_dst_mac,
				dst_ip=dst_ip)
			p = packet.Packet()
			p.add_protocol(e)
			p.add_protocol(a)
			p.serialize()
			return p
		else:
			e = self._build_ether(ether.ETH_TYPE_8021Q, _eth_src_mac, _eth_dst_mac)
			v = vlan.vlan(pcp=0,
			              cfi=0,
			              vid=vid,
			              ethertype=ether.ETH_TYPE_ARP)
			a = arp.arp(hwtype=1,
			            proto=ether.ETH_TYPE_IP,
			            hlen=6,
			            plen=4,
			            opcode=opcode,
			            src_mac=_eth_src_mac,
			            src_ip=src_ip,
			            dst_mac=_eth_dst_mac,
			            dst_ip=dst_ip)
			p = packet.Packet()
			p.add_protocol(e)
			p.add_protocol(v)
			p.add_protocol(a)
			p.serialize()
			return p

	def _find_protocol(self, pkt, name):
		# Buscar o protocolo pelo nome
		for p in pkt.protocols:
			if hasattr(p, 'protocol_name'):
				if p.protocol_name == name:
					return p

	def _arp_reply(self, src_ip, dst_ip, vid=None):
		# Construir o pacote de ARP_REPLY
		p = self._build_arp(arp.ARP_REPLY, dst_ip, src_ip, vid)
		if p is None:
			return None
		return p.data

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		# install table-miss flow entry
		#
		# We specify NO BUFFER to max_len of the output action due to
		# OVS bug. At this moment, if we specify a lesser number, e.g.,
		# 128, OVS will send Packet-In with invalid buffer_id and
		# truncated packet data. In that case, we cannot output packets
		# correctly.
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
						  ofproto.OFPCML_NO_BUFFER)]

		self.add_flow(datapath, 0, match, actions)

	def add_flow(self, datapath, priority, match, actions):
		"""
		 Adiciona a regra de fluxo no plano de dados associado
		"""
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

		mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
					idle_timeout=0, hard_timeout=0,
					match=match, instructions=inst)
		datapath.send_msg(mod)

	def delete_flow(self, datapath):
		"""
		 Deleta uma regra de fluxo no plano de dados associado
		"""
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		for dst in self.mac_to_port[datapath.id].keys():
			match = parser.OFPMatch(eth_dst=dst)
			mod = parser.OFPFlowMod(
				datapath, command=ofproto.OFPFC_DELETE,
				out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
				priority=1, match=match)
			datapath.send_msg(mod)

	def sync_rules(self):
		"""
		Sincroniza as regras em todos os nós
		"""
		for dp_aux in self.switches.dps.values():
			ofp_aux = dp_aux.ofproto
			parser_aux = dp_aux.ofproto_parser
			self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" ####### dpid=[%s] #######",dp_aux.id)
			for i in self.hypercube.nodes:
				if self.hypercube.nodes[i].dpid != dp_aux.id:
					res = self.hypercube.nodes[i].mac
					dst_dpid = self.hypercube.nodes[i].dpid
					#
					##
					# Captura o proximo dpid a ser alcancado para o destino específico
					next_dpid = self.hypercube.get_route(dp_aux.id, dst_dpid)[1]
					# Determina a porta de saída para o destino
					out_port = self.hypercube.nodes[dp_aux.id].neighbors[next_dpid].port_no
					# Monta a ação do Openflow 1.3
					actions = [parser_aux.OFPActionOutput(out_port)]
					match = parser_aux.OFPMatch(
						eth_dst=res)
					self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" dst_dpid=[%s] dst=[%s] outport=[%s]",
					                 dp_aux.id,
					                 Fore.WHITE+res+Fore.WHITE,
					                 out_port)
					self.hypercube.add_macToPort(int(dp_aux.id), res, out_port)
					self.add_flow(dp_aux, 10, match, actions)

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		# Abrir o protocolo OpenFlow
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']

		pkt = packet.Packet(msg.data)

		# Abrir o header Ethernet
		eth = pkt.get_protocols(ethernet.ethernet)[0]
		dst = eth.dst
		src = eth.src
		# Define o DPID do switch
		dpid = datapath.id

		p_arp  = self._find_protocol(pkt, "arp")
		p_vlan = self._find_protocol(pkt, "vlan")

		if p_arp:
			self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" Arp Protocol Received - ARP_Proxy Handle")
			if p_arp.opcode == arp.ARP_REQUEST:
				src_ip = str(netaddr.IPAddress(p_arp.src_ip))
				dst_ip = str(netaddr.IPAddress(p_arp.dst_ip))
				pkt_vlan = pkt.get_protocol(vlan.vlan)
				if p_vlan:
					data = self._arp_reply(src_ip, dst_ip, p_vlan.vid)
				else:
					data = self._arp_reply(src_ip, dst_ip, None)
				if data is None:
					return

				self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" ARP_Request Handle: [%s]->[%s]", src_ip, dst_ip)
				self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" Seek on DataBase")
				self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" Send Pkt ARP_Reply")
				self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" in_port=[%s]", in_port)
				if p_vlan:
					self.logger.info("--- PacketIn: vlan id=%s\n\n", p_vlan.vid)

				actions = [datapath.ofproto_parser.OFPActionOutput(in_port)]
				out_msg = datapath.ofproto_parser.OFPPacketOut(
				        datapath=datapath, buffer_id=0xffffffff, in_port=ofproto.OFPP_LOCAL,
				        actions=actions, data=data)
				datapath.send_msg(out_msg)

		else:
			eth = pkt.get_protocol(ethernet.ethernet)
			eth_dst = eth.dst
			eth_src = eth.src

			# Drop Link Layer Discovery Protocol packets
			if eth_dst == "01:80:c2:00:00:0e":
				return

			self.logger.info(Fore.CYAN+"[Packet In]"+Fore.WHITE+" dpid=[%s] src=[%s] dst=[%s] in_port=[%s]",
			                 dpid,
			                 Fore.WHITE+eth_src+Fore.WHITE, Fore.WHITE+eth_dst+Fore.WHITE,
			                 in_port)
			#self.hypercube.add_macToPort(dpid, eth_src, in_port)
			#out_port = self.hypercube.get_macToPort(dpid, eth_dst)

			d_dpid = int(eth_dst.split(':')[3]) + 1

			if(dpid != d_dpid):
				self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" ####### dpid=[%s] #######",dpid)
				for i in self.hypercube.nodes:
					if self.hypercube.nodes[i].dpid != dpid:
						# Monta os proximos destinos
						#res = eth_dst.split(':')
						#res[3] = str(self.hypercube.nodes[i].dpid - 1 ).zfill(2)
						#res = ":".join(res)
						res = self.hypercube.nodes[i].mac
						d_dpid = self.hypercube.nodes[i].dpid
						#
						##
						# Captura o proximo dpid a ser alcancado para o destino específico
						next_dpid = self.hypercube.get_route(dpid, d_dpid)[1]
						# Determina a porta de saída para o destino
						out_port = self.hypercube.nodes[dpid].neighbors[next_dpid].port_no
						# Monta a ação do Openflow 1.3
						actions = [parser.OFPActionOutput(out_port)]
						match = parser.OFPMatch(
							eth_dst=res)
						self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" dst_dpid=[%s] dst=[%s] outport=[%s]",
						                 d_dpid,
						                 Fore.WHITE+res+Fore.WHITE,
						                 out_port)
						self.hypercube.add_macToPort(dpid, res, out_port)
						self.add_flow(datapath, 10, match, actions)
			elif(dpid == d_dpid):
				out_port=1
				actions = [parser.OFPActionOutput(out_port)]
				match = parser.OFPMatch(
					#in_port=in_port,
					eth_dst=eth_dst)
				self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" ####### dpid=[%s] #######",dpid)
				self.logger.info(Fore.BLUE+"[Add Flow]"+Fore.WHITE+" dst_dpid=[%s] dst=[%s] outport=[%s]",
				                 d_dpid,
				                 Fore.WHITE+eth_dst+Fore.WHITE,
				                 out_port)
				self.hypercube.add_macToPort(dpid, eth_dst, out_port)
				self.add_flow(datapath, 10, match, actions)

	@set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER)
	def link_add_handler(self, ev):
		try:
			self.hypercube.add_link(ev.link)
			self.logger.info(Fore.MAGENTA+"[Change Topology] "+Fore.WHITE+"Link: SRC=[%s] DST=[%s] ["
			                 +Fore.GREEN+"UP"+Fore.WHITE+"]",
							                 ev.link.src.dpid,
							                 ev.link.dst.dpid)
			self.logger.info(Fore.MAGENTA+"[Change Topology] "+Fore.WHITE+"Syncing Rules")
			self.sync_rules()
		except Exception, ex:
			self.logger.info(Fore.RED+"[ERROR] %s"+Fore.WHITE, ex.message)

	@set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
	def link_delete_handler(self, ev):
		try:
			self.hypercube.del_link(ev.link)
			self.logger.info(Fore.MAGENTA+"[Change Topology] "+Fore.WHITE+"Link: SRC=[%s] DST=[%s] ["
			                 +Fore.RED+"DOWN"+Fore.WHITE+"]",
							                 ev.link.src.dpid,
							                 ev.link.dst.dpid)
			self.logger.info(Fore.MAGENTA+"[Change Topology] "+Fore.WHITE+"Syncing Rules")
			self.sync_rules()
		except Exception, ex:
			self.logger.info(Fore.RED+"[ERROR] %s"+Fore.WHITE, ex.message)