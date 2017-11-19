from packet import Packet
from packet_constructor import Packet_Constructor
import threading

class Packet_Sender:
    """
    Packet represents a simulated UDP packet.
    """
    #The next seq num for sent packets
    seq_num = 0
    #The next seq num for acks that we're waiting for
    next_seq_num = 0
    sent_packets = 0
    acked_packets = []
    acked_all_packets = False
    acked_packets_lock = threading.Lock()
    
    def reset():
        global seq_num
        global sent_packets
        global next_seq_num
        global acked_packets
        global acked_all_packets
        global acked_packets_lock
        seq_num = 0
        sent_packets = 0
        next_seq_num = 0
        acked_packets = []
        acked_all_packets = False
        acked_packets_lock = threading.Lock()
    
    def handle_ack(data):
        global acked_packets
        global seq_num
        global acked_all_packets
        global acked_packets_lock
        p = Packet.from_bytes(data)
        if not p.packet_type == Packet_Constructor.ack_type:
            #TODO: handle NAKs here
            return
        print("received ack " + str(p.seq_num))
        acked_packets_lock.acquire()
        if p.seq_num not in acked_packets:
            print("it's a new ack")
            acked_packets.append(p.seq_num)
            if len(acked_packets) == seq_num:
                print("got all acks")
                acked_all_packets = True
            else:
                print("len: " + str(len(acked_packets)))
                print("seq_num: " + str(seq_num))
        acked_packets_lock.release()
    
    #TODO: add timeouts. If we do not receive an ack in a certain period of time, resend the original packet
    #TODO: are there extra command line args we need to add?
    #TODO: anything else in pdf that we need to add?
    def await_acks(conn):
        print("awaitng acks")
        while not Packet_Sender.acked_all_packets:
            data, sender = conn.recvfrom(1024)
            threading.Thread(target=Packet_Sender.handle_ack, args=(data,)).start()
    
    @staticmethod
    def send_as_packets(data, conn, destination, peer_ip, peer_port):
        global sent_packets
        global acked_packets
        global next_seq_num
        global acked_all_packets
        global seq_num
        Packet_Sender.reset()
        max_payload_length = Packet.MAX_LEN - Packet.MIN_LEN
        
        curr = [0, 0]

        def nbytes(n):
            curr[0], curr[1] = curr[1], curr[1] + n
            return data[curr[0]: curr[1]]
        
        remaining_data = len(data)
        if remaining_data > 0:
            threading.Thread(target=Packet_Sender.await_acks, args=(conn,)).start()
        #While there's still data to be sent
        while remaining_data > 0:
            #While there are less packets in transit than the window size
            while sent_packets < Packet_Constructor.window_size:
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
                    seq_num += 1
                    print("remaining data " + str(remaining_data))
                    print("is last packet")
            #Update the number of packets still in transit
            while next_seq_num in acked_packets:
                next_seq_num += 1
                sent_packets -= 1
        print("Waiting for acks")
        while not acked_all_packets:
            #Wait here until all packets have been acked
            pass
        print("RECEIVED ALL ACKS")