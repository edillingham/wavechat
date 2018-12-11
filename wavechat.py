HEADER_SIZE = 44
CHAR_SIZE = 4410
WAV_HEADER_STRUCT = '4si4s4sihhiihh4si'
MAX_HEARTBEAT = 1024*1024*1
TERMINATOR = 32

class WaveChat:
    header_data = None
    char_map = {}   # wav data -> ord value
    map_char = None # ordinal value -> wav data

    def __init__(self):
        with open('all_notes.wav', 'rb') as wavfile:
            bs = wavfile.read()
        
        self.header_data = bs[:HEADER_SIZE]
        self.audio_data = bs[HEADER_SIZE + CHAR_SIZE:].lstrip() # skip the first chunk. not sure why
        
        # create a dict with the key as the chunk and the index as the value
        #print(self.audio_data)        
        the_chunks = self.chunks(self.audio_data, CHAR_SIZE)
        self.char_map = {c: i for i, c in enumerate(the_chunks)}
        self.map_char = {v: k for k, v in self.char_map.items()}
        
        #print(self.char_map)
        #print(self.map_char)

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def decode(self, bin_msg, strip_header=False):
        """Decode a string from wav data. Optionally strips the WAV header before decoding."""
        if strip_header:
            bin_data = bin_msg[HEADER_SIZE:]
        else:
            bin_data = bin_msg

        rw_list = []
        chunk_list = list(self.chunks(bin_data, CHAR_SIZE))
        for c in chunk_list:
            #char = c[0] # no idea how this happened...
            if c in self.char_map:# and self.char_map[c] != 0:
                rw_list.append(self.char_map[c])
    
        #print(rw_list)
        msg = ''.join([chr(c) for c in rw_list])
        return msg

    def encode(self, str_msg):
        """Encode a string to the wav data"""
        return b''.join([self.map_char[ord(c)] for c in str_msg])

    def export(self, filename, bindata):
        with open(filename, 'bw') as f:
            f.write(self.header_data)
            f.write(bindata)

if __name__ == '__main__':
    wc = WaveChat()

    # encode
    data = wc.encode('fuck you, assholio')
    wc.export('fuckyou.wav', data)

    # decode
    with open('fuckyou.wav', 'rb') as f:
        bdata = f.read()
    print(wc.decode(bdata, strip_header=True))
    