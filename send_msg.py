# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 15:17:05 2016

@author: Erik Dillingham
"""

import socket

IPADDR = '168.235.68.193'
PORTNUM = 5742
MAX = 65535
HEADERSIZE = 44
SAMPLESIZE = 4410

def recieveBytes(socket, packet=65535):
    byts = bytearray()
    while True:
        data = socket.recv(packet)
        if data == b'':
            break
        else:
            byts += data
            #print('read {}'.format(len(byts)))

    return byts

class WavHeader:
    def __init__(self, header_bytes):
        self.marker = header_bytes[0:4]
        self.filesize = header_bytes[4:8]
        self.filetype = header_bytes[8:12]
        self.format = header_bytes[12:16]
        self.format_length = header_bytes[16:20]
        self.format_type = header_bytes[20:22]
        self.num_channels = header_bytes[22:24]
        self.sample_rate1 = header_bytes[24:28]
        self.sample_rate2 = header_bytes[28:32]
        self.sample_rate3 = header_bytes[32:34]
        self.bits_per_sample = header_bytes[34:36]
        self.data_header = header_bytes[36:40]
        self.data_size = header_bytes[40:44]

    def __repr__(self):
        rep = """WavHeader:
        Marker:     {marker},
        Filesize:   {filesize},
        Filetype:   {filetype},
        Format:     {format},
        Fmt len:    {format_length},
        Fmt type:   {format_type},
        # channels: {num_channels},
        Samp. rate: {sample_rate1},
                    {sample_rate2},
                    {sample_rate3},
        bits/samp:  {bits_per_sample},
        data hdr:   {data_header},
        data size:  {data_size}
        """
        return (rep.format(**self.__dict__))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.connect((IPADDR, PORTNUM))
print('connected!')

data = bytearray(map(ord, "blow me"))
print('sending data..')
sock.send(data)

print('recieving data..')
byts = bytearray()
while True:
    data = sock.recv(MAX)
    if data == b'':
        break
    else:
        byts += data

print(byts[:44])

#sock.close()
#sock.send(data)

chars = {}
for i in range(0, 255):
    chars[i] = sock.recv(SAMPLESIZE)

senddata = b''.join([chars[ord(c)] for c in 'RIFFWAVE'])
sock.send(senddata)

#recieveToFile(sock, file='out.wav')

print('closing connection...')
sock.close()