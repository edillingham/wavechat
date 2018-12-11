# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 15:17:05 2016

@author: Erik Dillingham
"""

import socket
from struct import Struct
from wavechat import *


def receiveAllToFile(sckt, filename, packetsize=MAX_PACKET):
    with open(filename, 'wb') as outfile:
        while True:
            data = sckt.recv(packetsize)
            if data == b'':
                break
            else:
                outfile.write(data)

def receiveMaxToFile(sckt, filename, packetsize=MAX_PACKET, maxlength=MAX_HEARTBEAT):
    hblen = 0
    with open(filename, 'wb') as outfile:
        while hblen < maxlength:
            hbd = sckt.recv(packetsize)
            if hbd == b'':
                break
            else:
                outfile.write(hbd)
                hblen += len(hbd)
                
print('opening connection...')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.connect((IPADDR, PORTNUM))
print('connected!')

data = bytearray(map(ord, "fuck you"))
print('sending wakeup...')
sock.send(data)

print('loading lookup table...')
receiveAllToFile(sock, 'all_notes.wav')

print('closing connection...')
sock.close()

print('parsing lookup...')
with open('all_notes.wav', 'rb') as wavfile:
    bs = wavfile.read()

header_data = bs[:HEADER_SIZE]
audio_data = bs[HEADER_SIZE + CHAR_SIZE:].lstrip() # skip the first chunk. not sure why

# create a dict with the key as the chunk and the index as the value
char_map = {c: i for i, c in enumerate(chunks(audio_data, CHAR_SIZE))}
map_char = dict((v,k) for k, v in char_map.items())

# now use the lookup table to figure out what the heartbeat is saying
print('reopening connection...')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.connect((IPADDR, PORTNUM))
print('connected!')

#print ('writing heartbeat data...')
#receiveMaxToFile(sock, 'heartbeat.wav')
#
#print ('parsing heartbeat data...')
#with open('heartbeat.wav', 'rb') as hbfile:
#    hb_data = hbfile.read()
#
#hb_list = []
#for c in list(chunks(hb_data[HEADER_SIZE:], CHAR_SIZE)):
#    if c in char_map and c != '\x00':
#        hb_list.append(char_map[c])
#
#print('heartbeat:')        
#print(hb_list)

print('sending handshake...')
hs_data = b''.join([map_char[ord(c)] for c in "weevhy"])
sock.send(header_data + hs_data)

#with open('riffwave.wav', 'wb') as rwfile:
#    rwfile.write(header_data)
#    rwfile.write(hs_data)

in_str = None
the_slice = slice(HEADER_SIZE, None)
while True:
    receiveMaxToFile(sock, 'tmp.wav')
    with open('tmp.wav', 'rb') as rwfile:
        rw_data = rwfile.read()
    
    rw_list = []
    chunk_list = list(chunks(rw_data[the_slice], CHAR_SIZE))
    for c in chunk_list:
        if c in char_map:# and char_map[c] != 0:
            rw_list.append(char_map[c])

    print(rw_list)    
    print(''.join([chr(c) for c in rw_list]))

    in_str = input('>')
    if in_str.lower() == 'quit':
        break;

    in_str = in_str + '\n'
    print([ord(c) for c in in_str])
    hs_data = b''.join([map_char[ord(c)] for c in in_str])# if '\n' not in c])
    request = header_data + hs_data
    sock.send(request)

    with open('request.wav', 'wb') as reqfile:
        reqfile.write(request)

    the_slice = slice(None, None)
    
print('closing connection...')
sock.close()

# read/parse wav header. this is kind of neat
hdr = Struct(WAV_HEADER_STRUCT)
unpacked = list(hdr.unpack(header_data))
#unpacked = struct.unpack(WAV_HEADER_STRCUT, bs[:44])  # header = Struct(WAV_HEADER_STRUCT)
print(unpacked)
print(hdr.pack(*unpacked))

# god fucking damn it


