# Part 3 of UWCSE's Mininet-SDN project
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

log = core.getLogger()

# Convenience mappings of hostnames to ips
IPS = {
    "h10": "10.0.1.10",
    "h20": "10.0.2.20",
    "h30": "10.0.3.30",
    "serv1": "10.0.4.10",
    "hnotrust": "172.16.10.100",
}

# Convenience mappings of hostnames to subnets
SUBNETS = {
    "h10": "10.0.1.0/24",
    "h20": "10.0.2.0/24",
    "h30": "10.0.3.0/24",
    "serv1": "10.0.4.0/24",
    "hnotrust": "172.16.10.0/24",
}


class Part3Controller(object):
    """
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        log.debug(f"Connected to switch with DPID: {connection.dpid}")
        # Keep track of the connection to the switch so that we can send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        
        # Use the DPID to figure out which switch is being created
        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 21:
            self.cores21_setup()
        elif connection.dpid == 31:
            self.dcs31_setup()
        else:
            log.error("UNKNOWN SWITCH")
            exit(1)

    # Default flood rule
    def set_up_all(self):
        msg = of.ofp_flow_mod()
        action = of.ofp_action_output(port=of.OFPP_FLOOD)  # Flood all unmatched traffic
        msg.actions.append(action)
        self.connection.send(msg)
        log.debug("Default flood rule set for switch %s", self.connection.dpid)

    def s1_setup(self):
        log.debug("Setting up rules for switch 1")
        self.set_up_all()

    def s2_setup(self):
        log.debug("Setting up rules for switch 2")
        self.set_up_all()

    def s3_setup(self):
        log.debug("Setting up rules for switch 3")
        self.set_up_all()

    def cores21_setup(self):
        log.debug("Setting up rules for cores21 switch")

        # Block all ICMP traffic from hnotrust
        b1 = of.ofp_flow_mod()
        b1.match.nw_proto = 1  # ICMP protocol
        b1.match.dl_type = 0x0800  # IPv4
        b1.match.nw_src = IPS["hnotrust"]  # Source IP
        self.connection.send(b1)
        log.debug("Blocking ICMP from %s", IPS["hnotrust"])

        # Block all traffic from hnotrust to serv1
        b2 = of.ofp_flow_mod()
        b2.match.dl_type = 0x0800  # IPv4
        b2.match.nw_src = IPS["hnotrust"]  # Source IP
        b2.match.nw_dst = IPS["serv1"]  # Destination IP
        self.connection.send(b2)
        log.debug("Blocking traffic from %s to %s", IPS["hnotrust"], IPS["serv1"])

        # Allow traffic to host h10
        h1 = of.ofp_flow_mod()
        h1.match.dl_type = 0x0800  # IPv4
        h1.match.nw_dst = IPS["h10"]  # Destination IP
        h1.actions.append(of.ofp_action_output(port=1))  # Output to port 1
        self.connection.send(h1)
        log.debug("Allowing traffic to %s", IPS["h10"])
        
        # Allow traffic to host h20
        h2 = of.ofp_flow_mod()
        h2.match.dl_type = 0x0800  # IPv4
        h2.match.nw_dst = IPS["h20"]  # Destination IP
        h2.actions.append(of.ofp_action_output(port=2))  # Output to port 2
        self.connection.send(h2)
        log.debug("Allowing traffic to %s", IPS["h20"])
        
        # Allow traffic to host h30
        h3 = of.ofp_flow_mod()
        h3.match.dl_type = 0x0800  # IPv4
        h3.match.nw_dst = IPS["h30"]  # Destination IP
        h3.actions.append(of.ofp_action_output(port=3))  # Output to port 3
        self.connection.send(h3)
        log.debug("Allowing traffic to %s", IPS["h30"])

        # Allow traffic to serv1
        serv1 = of.ofp_flow_mod()
        serv1.match.dl_type = 0x0800  # IPv4
        serv1.match.nw_dst = IPS["serv1"]  # Destination IP
        serv1.actions.append(of.ofp_action_output(port=4))  # Output to port 4
        self.connection.send(serv1)
        log.debug("Allowing traffic to %s", IPS["serv1"])
        
        # Set up flooding for all other traffic
        self.set_up_all()

    def dcs31_setup(self):
        log.debug("Setting up rules for datacenter switch")
        self.set_up_all()

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        """
        Packets not handled by the router rules will be
        forwarded to this method to be handled by the controller
        """
        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        log.info("Unhandled packet from %s: %s", self.connection.dpid, packet.dump())


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s", event.connection)
        Part3Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
