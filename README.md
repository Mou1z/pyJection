# pyJection

**Disclaimer: I do not support or support, encourage or give consent to any unethical use of this code.**

This is a pyDivert-based class I wrote for easy TCP packet injection, mainly between a client-server connection. For-example a connection between an application running on our machine, to an external server. This works on a MITM (Man-In-The-Middle) arrangement and injects packets into a TCP stream, in either direction (from Client -> Server or Server -> Client). 

Currently, this class duplicates the previous packet and substitutes our payloads in it. This is the only reason it needs to wait for a relevant packet to inject. To clarify, a relevant packet would the a packet which has the direction in which we want to inject a packet.

Possible Improvements:
- Implement multi-threading and packet crafting from scratch instead of duplication, so it doesn't have to wait for a packet.

The `seq` and `ack` numbers are automatically adjusted for the upcoming packets (as long as the script is running), which means you don't have to worry about the connection becoming desynchronized. 

Example usage can be seen in the [example.py](https://github.com/Mou1z/pyJection/blob/main/example.py) script.

The `config.py` file contains a `FILTER_EXPRESSION` which can be used to capture specific packets - and, yes! the class supports multiple streams too. The class keeps track of the displacement in `seq`, `ack`, and `ident` values of all the TCP streams.

After the filter expression has been set, you can go ahead and write your own script. You don't necessary need to use a separate `config.py` file for it. I made it separate just to increase the readability.

You first need to create an instance of the PacketManager:
```py
manager = PacketManager()
```

We then need to create a function and assign it to the `runFunction` attribute of `manager`. Following is the structure of the run function which is recommended:
```py
def runFunction(packet, packetStream):
  # This is called whenever a packet is received
  # packet represents the WinDivert packet object

  # if condition
    # manager.injectAfter(your payloads in bytes here, ...);
  # else
    packetStream.send(packet) # don't forget to send the packet

manager.runFunction = runFunction  
```

To clarify, we have to call either `manager.injectAfter` or `packetStream.send`. This is because `injectAfter` has `packetStream.send` called inside it so using `send` twice would send a duplicate packet. In short, we don't use `packetStream.send()` when we have injected a packet, otherwise we have to. I know this can be improved, I continued to the C++ implementation of it so I'm currently not working on making this better.

The `processPacket()` method is called whenever a packet is received to record the packet stream information, and adjust its `seq`, `ack`, and `ident` if needed. It's important to note that `processPacket` is called before the `runFunction`.

Finally, we start the process:
```py
manager.start()
```

This process needs to keep running as long as the application-server connection is valid - if there's a gap between the seq and ack numbers, otherwise the connection might disconnect.
