import pydivert
from pydivert import Direction
from config import FILTER_EXPRESSION

class Stream:
    def __init__(self, ports):
        self.ports = ports

        self.syncD = [0, 0]
        self.identD = [0, 0]

    def __str__(self):
        return f'>> {self.ports} | {self.syncD} | {self.identD}'

class PacketManager:
    def __init__(self):
        self.streams = {}
        self.lastPacket = None
        self.runFunction = None
        self.packetQueue = []
    
    def start(self):
        with pydivert.WinDivert(FILTER_EXPRESSION) as packetStream: 
            self.packetStream = packetStream

            for packet in packetStream:
                self.processPacket(packet)

                if self.runFunction != None:
                    self.runFunction(packet, packetStream)

    def processPacket(self, packet):
        self.lastPacket = packet

        src_port = packet.tcp.src_port
        dst_port = packet.tcp.dst_port

        if packet.direction == Direction.OUTBOUND:
            if src_port in self.streams:
                stream = self.streams[src_port]

                packet.tcp.seq_num = (packet.tcp.seq_num + stream.syncD[0]) % 4294967295
                packet.tcp.ack_num = (packet.tcp.ack_num - stream.syncD[1]) % 4294967295

                packet.ipv4.ident = (packet.ipv4.ident + stream.identD[0]) % 65536
            else:
                self.streams[src_port] = Stream((src_port, dst_port))

        elif packet.direction == Direction.INBOUND:
            if dst_port in self.streams:
                stream = self.streams[dst_port]

                packet.tcp.seq_num = (packet.tcp.seq_num + stream.syncD[1]) % 4294967295
                packet.tcp.ack_num = (packet.tcp.ack_num - stream.syncD[0]) % 4294967295

                packet.ipv4.ident = (packet.ipv4.ident + stream.identD[1]) % 65536
            else:
                self.streams[dst_port] = Stream((dst_port, src_port))

    def injectAfter(self, *payloads):
        self.packetStream.send(self.lastPacket, True)

        for payload in payloads:
            packet = self.lastPacket
            newPacket = pydivert.Packet(packet.raw, packet.interface, packet.direction)
            newPayload = payload
            newPacket.tcp.payload = newPayload

            newPacket.tcp.seq_num += len(self.lastPacket.payload)
            newPacket.ipv4.ident = (newPacket.ipv4.ident + 1) % 65536

            if packet.direction == Direction.OUTBOUND:
                src_port = packet.tcp.src_port
                self.streams[src_port].syncD[0] += len(newPayload)
                self.streams[src_port].identD[0] += 1
            else:
                dst_port = packet.tcp.dst_port
                self.streams[dst_port].syncD[1] += len(newPayload)
                self.streams[dst_port].identD[1] += 1

            self.packetStream.send(newPacket, True)
            self.lastPacket = newPacket