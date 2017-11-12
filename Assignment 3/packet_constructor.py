from packet import Packet

class Packet_Constructor:
    """
    Packet represents a simulated UDP packet.
    """
    
    window_size = 10
    data_type = 0
    ack_type = 1
    syn_ack_type = 2
    syn_type = 3
    
    def __init__(self):
        self.payload = b''
        self.next_seq_num = 0
    
    def reset(self):
        self.payload = b''
        self.next_seq_num = 0
    
    def send_ack(self, conn, seq_num, destination, peer_ip_addr, peer_port):
        p = Packet(packet_type=Packet_Constructor.ack_type,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip_addr,
                   peer_port=peer_port,
                   is_last_packet=True,
                   payload=b'')
        print("sending ack " + str(seq_num))
        conn.sendto(p.to_bytes(), destination)
    
    def add_packet(self, p, conn, sender):
        if p.seq_num >= self.next_seq_num and p.seq_num <= (self.next_seq_num + Packet_Constructor.window_size):
            self.send_ack(conn, p.seq_num, sender, p.peer_ip_addr, p.peer_port)
            if p.seq_num == self.next_seq_num:
                self.next_seq_num += 1
                self.payload += p.payload
                if(p.is_last_packet):
                    payload = self.payload
                    self.reset()
                    return payload
            else:
                print("got out of order packet " + str(p.seq_num))
                #TODO: store the out of order packet somewhere
        else:
            print("got an out of window packet " + str(p.seq_num))
            #TODO: I think we send a NAK in this case? Or is it not even supposed to end up here?
        return None
    
    def await_acks(conn, sent_packets):
        print("awaitng acks")
        while(sent_packets > 0):
            data, sender = conn.recvfrom(1024)
            print("got ack")
            p = Packet.from_bytes(data)
            print(p.seq_num)
            sent_packets -= 1
    
    @staticmethod
    def send_as_packets(data, conn, destination, peer_ip, peer_port):
        max_payload_length = Packet.MAX_LEN - Packet.MIN_LEN
        
        curr = [0, 0]

        def nbytes(n):
            curr[0], curr[1] = curr[1], curr[1] + n
            return data[curr[0]: curr[1]]
        
        remaining_data = len(data)
        sent_packets = 0
        seq_num = 0
        while remaining_data > 0:
            print("sending packet %d"%seq_num)
            if remaining_data > max_payload_length:
                p = Packet(packet_type=Packet_Constructor.data_type,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=peer_port,
                   is_last_packet=False,
                   payload=nbytes(max_payload_length))
                
                conn.sendto(p.to_bytes(), destination)
                sent_packets += 1
                remaining_data -= max_payload_length
                seq_num += 1
                print("not last packet")
            else:
                p = Packet(packet_type=Packet_Constructor.data_type,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=peer_port,
                   is_last_packet=True,
                   payload=nbytes(remaining_data))
                
                conn.sendto(p.to_bytes(), destination)
                sent_packets += 1
                remaining_data -= remaining_data
                print("remaining data " + str(remaining_data))
                print("is last packet")
            if(sent_packets == Packet_Constructor.window_size or remaining_data == 0):
                Packet_Constructor.await_acks(conn, sent_packets)
                sent_packets = 0