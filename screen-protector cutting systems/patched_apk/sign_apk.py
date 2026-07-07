import os, zipfile, struct, hashlib, zlib, base64, datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import CertificateBuilder, NameOID, Name
import cryptography.x509 as x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import CertificateBuilder, NameOID, Name
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import datetime

WORK = r"D:\workspase\screen-protector cutting systems\patched_apk"
ORIGINAL = os.path.join(WORK, "original.apk")
KEY_DIR = os.path.join(WORK, "key")

import sys
PATCHED_DEX_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "patched_dex")
OUT_APK_NAME = sys.argv[2] if len(sys.argv) > 2 else "patched.apk"
OUT_APK = os.path.join(WORK, OUT_APK_NAME)

os.makedirs(KEY_DIR, exist_ok=True)
KEY_PATH = os.path.join(KEY_DIR, "key.pem")
CERT_PATH = os.path.join(KEY_DIR, "cert.pem")

# 1. Load or generate RSA key + self-signed cert
if os.path.exists(KEY_PATH) and os.path.exists(CERT_PATH):
    with open(KEY_PATH, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(CERT_PATH, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read())
    print("[*] Loaded existing key/cert")
else:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SA Telecom"),
        x509.NameAttribute(NameOID.COMMON_NAME, "SA Telecom"),
    ])
    cert = (
        CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .sign(private_key, hashes.SHA256())
    )
    with open(KEY_PATH, 'wb') as f:
        f.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))
    with open(CERT_PATH, 'wb') as f:
        f.write(cert.public_bytes(Encoding.PEM))
    print("[*] Generated new key/cert")

# 2. Read original APK, replace DEX files, drop META-INF
print("[*] Reading original APK and rebuilding...")
tmp_files = {}
with zipfile.ZipFile(ORIGINAL, 'r') as z:
    for item in z.infolist():
        if item.filename.startswith("META-INF/"):
            continue
        if item.filename in ("classes.dex", "classes2.dex", "classes3.dex"):
            # use patched version if present
            pd = os.path.join(PATCHED_DEX_DIR, item.filename)
            if os.path.exists(pd):
                with open(pd, 'rb') as pf:
                    tmp_files[item.filename] = pf.read()
                continue
        tmp_files[item.filename] = z.read(item.filename)

# 3. Write new unsigned APK
unsigned = os.path.join(WORK, "unsigned.apk")
with zipfile.ZipFile(unsigned, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in tmp_files.items():
        z.writestr(name, content)
print(f"[*] Wrote unsigned APK: {len(tmp_files)} entries")

# 4. Build v1 JAR signature (MANIFEST.MF, CERT.SF, CERT.RSA)
def sha256(b):
    return hashlib.sha256(b).digest()

manifest = b"Manifest-Version: 1.0\r\nCreated-By: SA Telecom\r\n\r\n"
sf_body = b"Signature-Version: 1.0\r\nCreated-By: SA Telecom\r\n"
import base64
def b64(d):
    return base64.b64encode(d).decode()

manifest_entries = b""
sf_entries = b""
# Re-open unsigned to compute digests in deterministic order
with zipfile.ZipFile(unsigned, 'r') as z:
    names = sorted(z.namelist())
    for name in names:
        data = z.read(name)
        digest = sha256(data)
        manifest_entries += b"\r\nName: " + name.encode() + b"\r\n"
        manifest_entries += b"SHA-256-Digest: " + b64(digest).encode() + b"\r\n"
        # CERT.SF section digest = digest of the manifest entry block for this name
        block = b"Name: " + name.encode() + b"\r\nSHA-256-Digest: " + b64(digest).encode() + b"\r\n"
        sf_entries += b"\r\n" + block
        sf_entries += b"SHA-256-Digest: " + b64(sha256(block)).encode() + b"\r\n"

manifest += manifest_entries
sf = sf_body + sf_entries

# CERT.RSA: PKCS#7 SignedData of the .SF file
cert_der = cert.public_bytes(Encoding.DER)
def build_pkcs7(sf_bytes, private_key, cert_der):
    from cryptography.hazmat.primitives.asymmetric import utils as a_utils
    # Build PKCS#7 SignedData manually
    # SignedData ::= SEQUENCE {
    #   version INTEGER (1),
    #   digestAlgorithms SET OF AlgorithmIdentifier,
    #   contentInfo ContentInfo,
    #   certificates [0] IMPLICIT SET OF Certificate,
    #   signerInfos SET OF SignerInfo }
    digest_algo = der_seq(der_oid("2.16.840.1.101.3.4.2.1"))  # SHA-256
    content_info = der_seq(der_oid("1.2.840.113549.1.7.2"), b"")  # data
    # We'll use a simpler approach: use cryptography's helper if available
    # Build ContentInfo for the .SF (type id-data 1.2.840.113549.1.7.1)
    econtent = der_seq(der_oid("1.2.840.113549.1.7.1"), der_octet(sf_bytes))
    # digest algorithms set
    da_set = der_set(digest_algo)
    # certificates
    cert_set = der_set(cert_der)
    # signer info
    sig = private_key.sign(sf_bytes, padding.PKCS1v15(), hashes.SHA256())
    signer_info = build_signer_info(cert, sig, sha256(sf_bytes))
    signed_data = der_seq(
        der_integer(1),
        da_set,
        econtent,
        der_implicit(0, cert_set),
        der_set(signer_info),
    )
    outer = der_seq(der_oid("1.2.840.113549.1.7.2"), der_octet(der_seq(signed_data)))
    return outer

# --- minimal DER helpers ---
def der_len(n):
    if n < 0x80:
        return bytes([n])
    out = bytearray()
    while n:
        out.insert(0, n & 0xFF); n >>= 8
    return bytes([0x80 | len(out)]) + bytes(out)

def der_seq(*items):
    body = b"".join(items)
    return b"\x30" + der_len(len(body)) + body

def der_set(*items):
    body = b"".join(items)
    return b"\x31" + der_len(len(body)) + body

def der_octet(data):
    return b"\x04" + der_len(len(data)) + data

def der_integer(n):
    # positive integer
    b = n.to_bytes((n.bit_length() + 7) // 8 or 1, 'big')
    if b[0] & 0x80:
        b = b'\x00' + b
    return b"\x02" + der_len(len(b)) + b

def der_oid(oid):
    # oid string -> DER
    parts = [int(x) for x in oid.split('.')]
    first = parts[0] * 40 + parts[1]
    body = bytes([first])
    for p in parts[2:]:
        if p == 0:
            body += b'\x00'
        else:
            vals = bytearray()
            while p:
                vals.insert(0, (p & 0x7F) | (0x80 if len(vals) else 0))
                p >>= 7
            body += bytes(vals)
    return b"\x06" + der_len(len(body)) + body

def der_implicit(tag, data):
    return bytes([0xA0 | tag]) + der_len(len(data)) + data

def der_ia5(s):
    return b"\x16" + der_len(len(s)) + s

def der_utf8(s):
    return b"\x0C" + der_len(len(s)) + s

def build_signer_info(cert, signature, message_digest):
    # SignerInfo ::= SEQUENCE {
    #   version INTEGER (1),
    #   issuerAndSerialNumber IssuerAndSerialNumber,
    #   digestAlgorithm AlgorithmIdentifier,
    #   authenticatedAttributes [0] IMPLICIT SET OF Attribute (optional, we skip),
    #   digestEncryptionAlgorithm AlgorithmIdentifier,
    #   encryptedDigest OCTET STRING,
    #   unauthenticatedAttributes [1] IMPLICIT SET OF Attribute (optional) }
    # We use authenticated attributes (required by Android v1 with our structure):
    # Actually Android v1 requires the digest of content in authenticated attrs.
    issuer = cert.issuer.public_bytes(Encoding.DER)
    serial = der_integer(cert.serial_number)
    issuer_and_serial = der_seq(issuer, serial)
    digest_algo = der_seq(der_oid("2.16.840.1.101.3.4.2.1"))
    enc_algo = der_seq(der_oid("1.2.840.113549.1.1.1"))  # rsaEncryption
    # authenticated attributes: SET {
    #   SEQUENCE { OID content-type, SET { OID data } },
    #   SEQUENCE { OID message-digest, SET { OCTET STRING digest } } }
    ct_attr = der_seq(der_oid("1.2.840.113549.1.9.3"), der_set(der_oid("1.2.840.113549.1.7.1")))
    md_attr = der_seq(der_oid("1.2.840.113549.1.9.4"), der_set(der_octet(message_digest)))
    authed = der_set(ct_attr, md_attr)
    # Signature must be over the DER-encoded authenticated attributes (not including the SET tag? Android signs the full SET)
    # Android signs the encoded authed attrs (with SET tag) but with EXPLICIT tag 0x31 replaced by 0x31? We sign the SET bytes.
    to_sign = authed  # standard: sign the SET OF attrs (tag 0x31)
    sig = private_key.sign(to_sign, padding.PKCS1v15(), hashes.SHA256())
    signer_info = der_seq(
        der_integer(1),
        issuer_and_serial,
        digest_algo,
        der_implicit(0, authed),
        enc_algo,
        der_octet(sig),
    )
    return signer_info

cert_rsa = build_pkcs7(sf, private_key, cert_der)

# 5. Assemble final APK: unsigned + META-INF
print("[*] Assembling signed APK...")
with zipfile.ZipFile(unsigned, 'r') as zin:
    with zipfile.ZipFile(OUT_APK, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            zout.writestr(item, zin.read(item.filename))
        zout.writestr("META-INF/MANIFEST.MF", manifest)
        zout.writestr("META-INF/CERT.SF", sf)
        zout.writestr("META-INF/CERT.RSA", cert_rsa)

print(f"[*] Wrote patched+signed APK: {OUT_APK}")
print(f"    Size: {os.path.getsize(OUT_APK)} bytes")
