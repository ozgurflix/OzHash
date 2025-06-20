import sys
import os
import base64
from main import OzHash 
config = {
    "matrix_size": 4,
    "memory_blocks": 2,
    "iterations": 5,
    "mod_bases": [257, 353],
    "memory_size": 512,
    "process_mode": "adaptive"
}

ozhash = OzHash(config)
password = "test123"
salt = ozhash.generate_salt()
seed = 12345

encoded = ozhash.encrypt(password, salt, seed)
verified = ozhash.verify("test123", encoded)
print(f"Verification: {verified}")