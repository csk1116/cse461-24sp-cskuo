# Part 2 of UWCSE's Project 3
#
# based on Lab 4 from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of

# Set up logging
log = core.getLogger()

class FirewallController(object):
    """
    A FirewallController object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        # Store the connection to the switch
        self.connection = connection
        # Bind our PacketIn event listener
        connection.addListeners(self)
        # Define the flood action once and reuse it
        flood_action = of.ofp_action_output(port=of.OFPP_FLOOD)

        # Create and send the flow mod message for ICMP traffic
        icmp_rule = of.ofp_flow_mod()
        icmp_rule.match.nw_proto = 1  # ICMP protocol
        icmp_rule.match.dl_type = 0x0800  # IPv4
        icmp_rule.actions.append(flood_action)
        self.connection.send(icmp_rule)

        # Create and send the flow mod message for ARP traffic
        arp_rule = of.ofp_flow_mod()
        arp_rule.match.dl_type = 0x0806  # ARP protocol
        arp_rule.actions.append(flood_action)
        self.connection.send(arp_rule)

    def _handle_PacketIn(self, event):
        """
        Handle packets that are not matched by existing flow rules.
        """

        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp
        print("Unhandled packet: " + str(packet.dump()))

def launch():
    """
    Starts the component and sets up event listener for switch connections.
    """
    
    def handle_connection_up(event):
        log.debug("Controlling %s" % (event.connection,))
        FirewallController(event.connection)

    # Add a listener for when switches connect to the controller
    core.openflow.addListenerByName("ConnectionUp", handle_connection_up)
