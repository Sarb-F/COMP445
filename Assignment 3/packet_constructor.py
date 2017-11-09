from packet import Packet

class Packet_Constructor:
    """
    Packet represents a simulated UDP packet.
    """

    def __init__(self):
        self.payload = b''
        self.next_seq_num = 0
    
    def reset(self):
        self.payload = b''
        self.next_seq_num = 0
    
    def add_packet(self, p):
        if p.seq_num == self.next_seq_num:
            self.next_seq_num += 1
            self.payload += p.payload
            if(p.is_last_packet):
                payload = self.payload
                self.reset()
                return payload
        return None