from Pyfhel import Pyfhel, PyCtxt
import numpy as np


class HEManager:
    def __init__(self):
        self.HE = Pyfhel()
        self.bfv_params = {
            "scheme": "BFV",  # Use the BFV homomorphic encryption scheme
            "n": 2
            ** 13,  # Polynomial modulus degree (8192); affects security and ciphertext size
            "t": 65537,  # Plaintext modulus; determines the range of plaintext values
            "sec": 128,  # Security level in bits (128 bits is standard)
        }
        self.HE.contextGen(**self.bfv_params)
        self.HE.keyGen()

    def encrypt(self, plaintext: str):
        # Convert string to array of ints (unicode code points)
        arr = np.array([ord(c) for c in plaintext], dtype=np.int64)
        ptxt = self.HE.encodeInt(arr)
        ctxt = self.HE.encryptPtxt(ptxt)
        print(f"encrypted ver: {ctxt}")
        return ctxt.to_bytes()

    def decrypt(self, ctxt_bytes):
        ctxt = PyCtxt(pyfhel=self.HE, bytestring=ctxt_bytes)
        arr = self.HE.decryptInt(ctxt)
        # Remove trailing zeros (from encoding padding)
        arr = [i for i in arr if i != 0]
        return "".join([chr(i) for i in arr])


# Example usage:
if __name__ == "__main__":
    he = HEManager()
    secret = "hello"
    enc = he.encrypt(secret)
    dec = he.decrypt(enc)
    print("Original:", secret)
    print("Decrypted:", dec)