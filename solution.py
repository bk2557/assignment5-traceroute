
from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # dummy header with 0 checksum
    ID = os.getpid() & 0xFFF
    # struct - interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)

    # put checksum into header

    if sys.platform == 'darwin':
        # convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xfff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    # Don’t send the packet yet , just return the final packet in this function.
    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    # tracelist1 = [] #This is your list to use when iterating through each trace
    tracelist2 = [] #This is your list to contain all traces

    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            tracelist1 = []  # This is your list to use when iterating through each trace
            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    # SHOULD I APPEND THE OTHER VALUES BEFORE THE REQUEST TIMEOUT VERBAGE? 1. RTT IP REQUEST TIMED OUT?
                    tracelist1.insert(0, "*")
                    tracelist1.insert(0, str(ttl))
                    tracelist2.append(tracelist1)
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    #You should add the list above to your all traces list
                    tracelist1.insert(0, "*")
                    tracelist1.insert(0, str(ttl))
                    tracelist2.append(tracelist1)
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmp = recvPacket [20:28]
                #bytes = struct.calcsize("d")
                #icmpType = struct.unpack("d", recvPacket[20:20 + bytes])[0]
                type, code, checksum, id, sequence = struct.unpack("bbHHh", icmp)
                types = type
                # return type
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    pingHost = gethostbyaddr(addr[0])
                    # tracelist1.append(pingHost)
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    pingHost = "hostname not returnable"
                    #tracelist1.append("hostname not returnable")
                    #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +
                    bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    rtt = (timeReceived - startedSelect) * 1000
                    tracelist1.insert(0, str(pingHost[0]))
                    tracelist1.insert(0, str(addr[0]))
                    tracelist1.insert(0, str(round(rtt)) + 'ms')
                    tracelist1.insert(0, str(ttl))
                    tracelist2.append(tracelist1)
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    tracelist1.append("Destination Unreachable")
                    tracelist1.insert(0, "*")
                    tracelist1.insert(0, str(ttl))
                    tracelist2.append(tracelist1)
                    #print(tracelist2)
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    rtt = (timeReceived - startedSelect) * 1000
                    tracelist1.insert(0, str(pingHost[0]))
                    tracelist1.insert(0, str(addr[0]))
                    tracelist1.insert(0, str(round(rtt)) + 'ms')
                    tracelist1.insert(0, str(ttl))
                    tracelist2.append(tracelist1)
                    #print(tracelist2)
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1.append("Exception/Error")
                    tracelist2.append(tracelist1)
                    tracelist1.insert(0, str(ttl))
                    #print(tracelist2)
                    #Fill in end
                break

            finally:
                mySocket.close()
        print(tracelist2)
    return tracelist2


if __name__ == '__main__':
    get_route("google.co.il")
