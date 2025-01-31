from pydivert import Direction
from PacketManager import PacketManager

# Create an instance
manager = PacketManager()

# The remaining code is very flexible, 
# I'm creating a boolean variable here just to
# make sure only a single packet is injected
injected = False

def runFunction(packet, packetStream):
    global injected

    # Inject after an inbound packet because I want to inject in the inbound direction.
    # Some additional checks as well, in case there are multiple streams and I want to capture a specific one based on the contents of the payload.
    if not injected and packet.direction == Direction.INBOUND and \
        len(packet.payload) > 1 and packet.payload[1] == 3: 
        
        print('Injecting payload...')
        manager.injectPacketAfter(b'your payload data here')
        injected = True
        print('Injected Successfully!')
    else:
        packetStream.send(packet, True)

# We assign the function here
manager.runFunction = runFunction
manager.start() # Start!

# Note: Stopping the program ends the seq/ack virtual syncronization, therefore it can disconnect or disrupt the original connection in case there is a gap in seq/ack numbers.