"""
					for i in self.hypercube.nodes:
						if self.hypercube.nodes[i].dpid != int(dpid_str):
							res = self.hypercube.nodes[i].mac
							dst_dpid = self.hypercube.nodes[i].dpid
							#
							##
							# Captura o proximo dpid a ser alcancado para o destino específico
							next_dpid = self.hypercube.get_route(int(dpid_str), dst_dpid)[1]
							# Determina a porta de saída para o destino
							out_port = self.hypercube.nodes[int(dpid_str)].neighbors[next_dpid].port_no
							# Monta a ação do Openflow 1.3
							actions = [parser_n1.OFPActionOutput(out_port)]
							match = parser_n1.OFPMatch(
								eth_dst=res)
							self.logger.info(Fore.LIGHTBLUE_EX+"[Add Flow]"+Fore.WHITE+" dst_dpid=[%s] dst=[%s] outport=[%s]",
							                 int(dpid_str),
							                 Fore.LIGHTWHITE_EX+res+Fore.WHITE,
							                 out_port)
							self.hypercube.add_macToPort(int(dpid_str), res, out_port)
							self.add_flow(dp_n1, 10, match, actions)

					for i in self.hypercube.nodes:
						if self.hypercube.nodes[i].dpid != int(d_dpid):
							# Monta os proximos destinos
							#res = eth_dst.split(':')
							#res[3] = str(self.hypercube.nodes[i].dpid - 1 ).zfill(2)
							#res = ":".join(res)
							res = self.hypercube.nodes[i].mac
							dst_dpid = self.hypercube.nodes[i].dpid
							#
							##
							# Captura o proximo dpid a ser alcancado para o destino específico
							next_dpid = self.hypercube.get_route(int(d_dpid), dst_dpid)[1]
							# Determina a porta de saída para o destino
							out_port = self.hypercube.nodes[int(d_dpid)].neighbors[next_dpid].port_no
							# Monta a ação do Openflow 1.3
							actions = [parser_n2.OFPActionOutput(out_port)]
							match = parser_n2.OFPMatch(
								eth_dst=res)
							self.logger.info(Fore.LIGHTBLUE_EX+"[Add Flow]"+Fore.WHITE+" dst_dpid=[%s] dst=[%s] outport=[%s]",
							                 d_dpid,
							                 Fore.LIGHTWHITE_EX+res+Fore.WHITE,
							                 out_port)
							self.hypercube.add_macToPort(int(d_dpid), res, out_port)
							self.add_flow(dp_n2, 10, match, actions)

"""

"""
	@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
	def port_status_handler(self, ev):
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		# Convert DPID to String
		dpid_str = dpid_lib.dpid_to_str(dp.id)

		if msg.reason == ofp.OFPPR_ADD:
			reason = Fore.YELLOW+'ADD'+Fore.WHITE
		elif msg.reason == ofp.OFPPR_DELETE:
			reason = Fore.YELLOW+'DELETE'+Fore.WHITE
		elif msg.reason == ofp.OFPPR_MODIFY:
			reason = Fore.YELLOW+'MODIFY'+Fore.WHITE
		else:
			reason = Fore.YELLOW+'UNKNOWN'+Fore.WHITE

		if msg.desc.state == 1:
			state = Fore.RED+'DOWN'+Fore.WHITE
		elif msg.desc.state == 0:
			state = Fore.GREEN+'UP'+Fore.WHITE
			self.nodes_restore.append(dp.id)
		else:
			state = Fore.ORANGE+'UNKNOWN'+Fore.WHITE

		self.logger.info(Fore.MAGENTA+"[Port State Change]"+Fore.WHITE+" dpid=[%s] msg=[%s] port=[%s] state=[%s]",
		                  int(dpid_str), reason, msg.desc.port_no, state)

		d_dpid = None
		try:
			if msg.desc.state == 1:
				for d_dpid in self.hypercube.nodes[int(dpid_str)].neighbors:
					if(self.hypercube.nodes[int(dpid_str)].neighbors[d_dpid].port_no == msg.desc.port_no):
						self.logger.info("[Change Topology] Change Topology Handle")
						self.logger.info("[Change Topology] Link SRC_DPID=%s DST_DPID=%s",int(dpid_str), d_dpid )
						if msg.desc.state == 1:
							self.hypercube.fail_nodes(int(dpid_str), d_dpid)
						else:
							pass
						self.logger.info("[Change Topology] New Neighbors DPID=%s %s",
						                 int(dpid_str),self.hypercube.nodes[int(dpid_str)].neighbors)
						self.logger.info("[Change Topology] New Neighbors DPID=%s %s",
						                 d_dpid,self.hypercube.nodes[d_dpid].neighbors)

						self.sync_rules()
						break
			elif msg.desc.state == 0:
				if(len(self.nodes_restore) == 2):
					self.logger.info("[Change Topology] Change Topology Handle")
					self.logger.info("[Change Topology] Link SRC_DPID=%s DST_DPID=%s",
					                 self.nodes_restore[1], self.nodes_restore[0] )
					self.hypercube.restore_nodes(self.nodes_restore[1], self.nodes_restore[0])
					self.logger.info("[Change Topology] New Neighbors DPID=%s %s",
					                 self.nodes_restore[1],self.hypercube.nodes[self.nodes_restore[1]].neighbors)
					self.logger.info("[Change Topology] New Neighbors DPID=%s %s",
					                 self.nodes_restore[0],self.hypercube.nodes[self.nodes_restore[0]].neighbors)
					self.sync_rules()
				elif(len(self.nodes_restore)==3):
					self.nodes_restore = self.nodes_restore[-1:]
		except Exception, ex:
			self.logger.info("[ERROR] %s", ex.message)
"""

"""__author__ = 'rafael'

		# Lista os protocolos no header
		header_list = dict(
            (p.protocol_name, p)for p in pkt.protocols if type(p) != str)

		# Verifica se existe o protocolo ARP no header
		if ARP in header_list:
			self.arp_table[header_list[ARP].src_ip] = src  # ARP learning


		self.mac_to_port.setdefault(dpid, {})
		#self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

		# learn a mac address to avoid FLOOD next time.
		self.mac_to_port[dpid][src] = in_port
		print self.mac_to_port

		if dst in self.mac_to_port[dpid]:
			out_port = self.mac_to_port[dpid][dst]
		else:
			if self.arp_handler(header_list, datapath, in_port, msg.buffer_id):
				# 1:reply or drop;  0: flood
				self.logger.info("ARP_PROXY: packet in DPID[%s] %s %s IN_PORT[%s]", dpid, src, dst, in_port)
				return None
			else:
				out_port = ofproto.OFPP_FLOOD

		actions = [parser.OFPActionOutput(out_port)]

		# install a flow to avoid packet_in next time
		if out_port != ofproto.OFPP_FLOOD:
			match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
			self.add_flow(datapath, 1, match, actions)

		data = None
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data
		out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
		datapath.send_msg(out)

		"""
"""
	def arp_handler(self, header_list, datapath, in_port, msg_buffer_id):
		header_list = header_list
		datapath = datapath
		in_port = in_port

		if ETHERNET in header_list:
			eth_dst = header_list[ETHERNET].dst
			eth_src = header_list[ETHERNET].src

		if eth_dst == ETHERNET_MULTICAST and ARP in header_list:
			arp_dst_ip = header_list[ARP].dst_ip
			if (datapath.id, eth_src, arp_dst_ip) in self.sw:  # Break the loop
				if self.sw[(datapath.id, eth_src, arp_dst_ip)] != in_port:
					out = datapath.ofproto_parser.OFPPacketOut(
					    datapath=datapath,
					    buffer_id=datapath.ofproto.OFP_NO_BUFFER,
					    in_port=in_port,
					    actions=[], data=None)
					datapath.send_msg(out)
					return True
			else:
				self.sw[(datapath.id, eth_src, arp_dst_ip)] = in_port

		if ARP in header_list:
			hwtype = header_list[ARP].hwtype
			proto = header_list[ARP].proto
			hlen = header_list[ARP].hlen
			plen = header_list[ARP].plen
			opcode = header_list[ARP].opcode

			arp_src_ip = header_list[ARP].src_ip
			arp_dst_ip = header_list[ARP].dst_ip

			actions = []

			if opcode == arp.ARP_REQUEST:
				if arp_dst_ip in self.arp_table:  # arp reply
					actions.append(datapath.ofproto_parser.OFPActionOutput(
			            in_port)
			        )

					ARP_Reply = packet.Packet()
					ARP_Reply.add_protocol(ethernet.ethernet(
					    ethertype=header_list[ETHERNET].ethertype,
					    dst=eth_src,
					    src=self.arp_table[arp_dst_ip]))
					ARP_Reply.add_protocol(arp.arp(
					    opcode=arp.ARP_REPLY,
					    src_mac=self.arp_table[arp_dst_ip],
					    src_ip=arp_dst_ip,
					    dst_mac=eth_src,
					    dst_ip=arp_src_ip))

					ARP_Reply.serialize()

					out = datapath.ofproto_parser.OFPPacketOut(
					    datapath=datapath,
					    buffer_id=datapath.ofproto.OFP_NO_BUFFER,
					    in_port=datapath.ofproto.OFPP_CONTROLLER,
					    actions=actions, data=ARP_Reply.data)
					datapath.send_msg(out)
					return True
		return False"""
