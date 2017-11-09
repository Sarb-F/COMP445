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
        else:
            print("got out of order packet")
        return None
    
    @staticmethod
    def send_as_packets(data, conn, destination, peer_ip, peer_port):
        max_payload_length = Packet.MAX_LEN - Packet.MIN_LEN
        
        curr = [0, 0]

        def nbytes(n):
            curr[0], curr[1] = curr[1], curr[1] + n
            return data[curr[0]: curr[1]]
        
        remaining_data = len(data)
        seq_num = 0
        while remaining_data > 0:
            print("sending packet %d"%seq_num)
            if remaining_data > max_payload_length:
                p = Packet(packet_type=0,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=peer_port,
                   is_last_packet=False,
                   payload=nbytes(max_payload_length))
                
                conn.sendto(p.to_bytes(), destination)
                remaining_data -= max_payload_length
                seq_num += 1
                print("not last packet")
            else:
                p = Packet(packet_type=0,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=peer_port,
                   is_last_packet=True,
                   payload=nbytes(remaining_data))
                
                conn.sendto(p.to_bytes(), destination)
                remaining_data -= max_payload_length
                print("is last packet")