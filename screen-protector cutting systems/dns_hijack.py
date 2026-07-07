"""
SA Telecom - DNS Hijack for cutting machine (NO app install needed)
Run as ADMIN:  python dns_hijack.py
Intercepts the machine's DNS queries for the cloud domains and answers with
the local PC IP (192.168.0.101) so the STOCK app talks to our local server.

Domains hijacked:
  app.mietubl.com                 -> API  (served at /api/... by local Flask)
  mietubl.oss-accelerate.aliyuncs.com -> PLT (served at /model/... by local Flask)
  app.mobile-films.com            -> API (alt brand)
  mobile-films.oss-cn-hongkong.aliyuncs.com -> PLT (alt brand)
  api.hsyunqiemo.com              -> legacy cloud (safety)

Requirements:
  - Run on the PC that runs the local Flask server (app.py) on port 5000.
  - Machine must use this PC as its DNS server (set on machine WiFi, or ARP-spoof).
  - Windows: run in an elevated (Admin) PowerShell.
"""
import socket, struct, threading, os, sys

PC_IP = "192.168.0.101"   # <-- change to your PC's actual LAN IP
DNS_PORT = 53

HIJACK = {
    b"app.mietubl.com": PC_IP,
    b"mietubl.oss-accelerate.aliyuncs.com": PC_IP,
    b"app.mobile-films.com": PC_IP,
    b"mobile-films.oss-cn-hongkong.aliyuncs.com": PC_IP,
    b"api.hsyunqiemo.com": PC_IP,
}

def build_response(data, ip):
    # DNS header
    tid = data[0:2]
    flags = b"\x81\x80"          # QR=1, AA=1, RD=1, RA=1, no error
    qdcount = struct.unpack(">H", data[4:6])[0]
    ancount = struct.pack(">H", 1)
    header = tid + flags + data[4:6] + ancount + b"\x00\x00" + b"\x00\x00"
    # copy question
    q = data[12:]
    # find end of question (QNAME ends with 0x00, then QTYPE(2)+QCLASS(2))
    pos = 0
    while q[pos] != 0:
        pos += q[pos] + 1
    pos += 1  # null terminator
    question = q[:pos+4]
    # answer: pointer to question name (0xC00C), A record
    # NAME: pointer to 0x0C (offset of question in message)
    ans_name = b"\xc0\x0c"
    ans_type = b"\x00\x01"      # A
    ans_class = b"\x00\x01"     # IN
    ans_ttl = struct.pack(">I", 60)
    ans_rdlen = b"\x00\x04"
    ans_rdata = socket.inet_aton(ip)
    answer = ans_name + ans_type + ans_class + ans_ttl + ans_rdlen + ans_rdata
    return header + question + answer

def extract_qname(data):
    pos = 12
    labels = []
    while data[pos] != 0:
        l = data[pos]
        labels.append(data[pos+1:pos+1+l])
        pos += l + 1
    qname = b".".join(labels)
    return qname.lower()

def handle(sock):
    while True:
        try:
            data, addr = sock.recvfrom(4096)
        except Exception:
            break
        if len(data) < 12:
            continue
        qname = extract_qname(data)
        ip = None
        for dom, target in HIJACK.items():
            if qname == dom or qname.endswith(b"." + dom) or dom in qname:
                ip = target
                break
        if ip:
            try:
                resp = build_response(data, ip)
                sock.sendto(resp, addr)
                print(f"[HIJACK] {qname.decode()} -> {ip}  ({addr[0]})")
            except Exception as e:
                print("send err", e)
        else:
            # not ours; could forward to real DNS, but we just drop to avoid leak
            pass

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", DNS_PORT))
    except PermissionError:
        print("ERROR: bind port 53 failed. Run as ADMINISTRATOR.")
        sys.exit(1)
    print(f"SA Telecom DNS hijack listening on UDP/53 -> {PC_IP}")
    print("Hijacking:", [d.decode() for d in HIJACK])
    print("Make sure the machine uses this PC as its DNS server.")
    handle(sock)

if __name__ == "__main__":
    main()
