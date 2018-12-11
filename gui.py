# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 09:47:11 2016

@author: Erik Dillingham

wavechat GUI
"""

import tkinter as tk
import socket
import wavechat

IPADDR = '168.235.68.193'
PORTNUM = 5742
MAX_PACKET = 65535/4

class App:

    def __init__(self, master):
        self._handshake = False
        self._nick = None

        self.master = master

        frame = tk.Frame(master)
        frame.pack()

        self.inputText = tk.StringVar(frame, "")
        self.outputText = tk.StringVar(frame, "")

        self.output_textbox = tk.Text(frame)
        self.output_textbox.pack(side=tk.TOP)
        
        self.input_textbox = tk.Entry(frame, textvariable=self.inputText)
        self.input_textbox.pack(side=tk.LEFT)
        
        self.send_button = tk.Button(frame, text="Send", command=self.send_msg)
        self.send_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.pack(side=tk.LEFT)

        self._wavechat = wavechat.WaveChat()
        self._sending = False

    def __enter__(self):
        print('opening connection...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.connect((IPADDR, PORTNUM))
        print('connected!')

        print('handshaking...')
        hsdata = ''
        while not self._handshake:
            hsdata += self._wavechat.decode(self.read_data())
            if('RIFFWAVE' in hsdata):
                print('got handshake')
                self._handshake = True
        
        self.sock.send(self._wavechat.header_data)
        return self

    def __exit__(self, *exception_data):
        if exception_data[0]:
            print(exception_data)
            
        print('closing connection...')
        self.sock.close()

    def is_sending(self):
        return self._sending

    def read_data(self, packet_size=wavechat.CHAR_SIZE, max_packet=MAX_PACKET):
        datalen = 0
        alldata = b''
        while datalen < max_packet:
            packet = self.sock.recv(packet_size)
            if packet == b'':
                break
            else:
                alldata += packet
                datalen += len(packet)
        return alldata

    def send_msg(self):
        self._sending = True

        # first message is always the chosen nick
        raw_msg = self.inputText.get()
        
        if not self._nick:
            self._nick = raw_msg
            msg = "{}\n* you are now known as '{}'\n".format(raw_msg, self._nick)
        else:
            msg = '<{}> {}\n'.format(self._nick, raw_msg)
        
        self.write_output(msg)
        #print("sending {}".format(msg))
        
        msgdata = self._wavechat.encode("{}\n".format(raw_msg))
        #self._wavechat.export('message.wav', msgdata)
        self.sock.send(msgdata)
        
        self._sending = False
        self.inputText.set('')

    def write_output(self, text):
        self.output_textbox.insert(tk.END, "{}".format(text))
        
    def decode_and_show(self, encoded_msg):
        self.write_output(self._wavechat.decode(encoded_msg))


try:
    def data_loop(app):
        if not app.is_sending():
            msg = app.read_data()
            message = app._wavechat.decode(msg).strip('')
            for ch in message:
                if ord(ch) != 0:
                    app.write_output(ch)

        app.master.after(250, lambda: data_loop(app))
    
    root = tk.Tk()
    with App(root) as app:
        data_loop(app)    
        root.mainloop()

except:
    pass

finally:
    root.destroy()
