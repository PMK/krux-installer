# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
signer.py
"""
import re
import hashlib

from .base_signer import BaseSigner

ASN1_STRUCTURE_FOR_PUBKEY = "3036301006072A8648CE3D020106052B8104000A032200"
"""
ASN.1 STRUCTURE FOR PUBKEY (uncompressed and compressed):
   30  <-- declares the start of an ASN.1 sequence
   56  <-- length of following sequence (dez 86)
   30  <-- length declaration is following
   10  <-- length of integer in bytes (dez 16)
   06  <-- declares the start of an "octet string"
   07  <-- length of integer in bytes (dez 7)
   2A 86 48 CE 3D 02 01 <-- Object Identifier: 1.2.840.10045.2.1
                            = ecPublicKey, ANSI X9.62 public key type
   06  <-- declares the start of an "octet string"
   05  <-- length of integer in bytes (dez 5)
   2B 81 04 00 0A <-- Object Identifier: 1.3.132.0.10
                      = secp256k1, SECG (Certicom) named eliptic curve
   03  <-- declares the start of an "octet string"
   42  <-- length of bit string to follow (66 bytes)
   00  <-- Start pubkey?? 
"""


class TriggerSigner(BaseSigner):
    """
    Signer is the class that manages the `sign` command.
    """

    def __init__(self, filename: str):
        super().__init__(filename=filename)

    def make_hash(self):
        """Create a file hash before sign"""
        with open(self.filename, "rb") as f_sig:
            _bytes = f_sig.read()
            data = hashlib.sha256(_bytes).hexdigest()
            self.filehash = data

    def save_hash(self):
        """Save file's hash in a sha256.txt file"""
        if self.filehash is None:
            raise ValueError(f"Empty hash: {self.filehash}")

        if re.findall(r"^[a-f0-9]{64}$", self.filehash):
            filehashname = f"{self.filename}.sha256.txt"
            with open(filehashname, mode="w", encoding="utf-8") as h_file:
                content = f"{self.filehash} {self.filename}"
                h_file.write(content)
                print("")
                print("=====================")
                print(f"{filehashname} saved")
                print("=====================")
                print("")
        else:
            raise ValueError(f"Invalid hash: '{self.filehash}'")

    def save_signature(self):
        """Save the signature data into a .sig file"""
        if not self.signature is None:
            sigfile = f"{self.filename}.sig"
            with open(sigfile, "wb") as s_file:
                s_file.write(self.signature)
                print("")
                print("=====================")
                print(f"{sigfile} saved")
                print("=====================")
                print("")
        else:
            raise ValueError("Empty signature")

    def save_pubkey(self):
        """Create PEM data"""
        if not self.pubkey is None:
            # Format pubkey
            formated_pubkey = "\n".join(
                [
                    "-----BEGIN PUBLIC KEY-----",
                    self.pubkey,
                    "-----END PUBLIC KEY-----",
                ]
            )
            pubfile = f"{self.filename}.pem"
            with open(pubfile, mode="w", encoding="utf-8") as pb_file:
                pb_file.write(formated_pubkey)
                print("")
                print("=====================")
                print(f"{pubfile} saved")
                print("=====================")
                print("")
        else:
            raise ValueError(f"Empty pubkey: {self.pubkey}")
