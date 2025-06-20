# main.py
import numpy as np
import secrets
import os
import base64
from matrix_operations import MatrixHandler
from memory_manager import MemoryBlocks
from key_schedule import KeyScheduler
from errors import ConfigurationError, MemoryError, EncryptionError, VerificationError, OzHashError

class OzHash:
    def __init__(self, config):
        try:
            self.matrix_size = config.get("matrix_size", 16)
            self.memory_blocks_count = config.get("memory_blocks", 8) 
            self.iterations = config.get("iterations", 10)
            self.mod_bases = config.get("mod_bases", [257, 353, 509])
            self.memory_size = config.get("memory_size", 1024)
            self.process_mode = config.get("process_mode", "adaptive")

            if not isinstance(self.matrix_size, int) or self.matrix_size <= 0:
                raise ConfigurationError("Matrix size must be a positive integer.")
            if not isinstance(self.memory_blocks_count, int) or self.memory_blocks_count <= 0:
                raise ConfigurationError("Memory blocks count must be a positive integer.")
            if self.process_mode not in ["independent", "dependent", "adaptive"]:
                raise ConfigurationError("Invalid process mode.")

            # MemoryManager'ı start kısmı
            self.memory_manager = MemoryBlocks(self.memory_blocks_count, self.matrix_size, self.mod_bases, self.memory_size)
            
            # MemoryManagerden key'e iletelim.
            self.matrix_handler = MatrixHandler(self.matrix_size, self.mod_bases, self.memory_size, memory_manager=self.memory_manager)
            self.key_scheduler = KeyScheduler(self.mod_bases, self.memory_size, memory_manager=self.memory_manager)

        except Exception as e:
            raise ConfigurationError(f"Initialization failed: {e}")

    def generate_salt(self, length=16):
        try:
            return secrets.token_bytes(length) # secrets modülü daha güvenli
        except Exception as e:
            raise MemoryError(f"Salt generation failed: {e}")

    def _set_rng_seed(self, seed: int):
        """Tüm numpy rastgeleliklerini verilen tohumla başlatır."""
        seed_32bit = seed % (2**32) # sınır şimdilik 2**32
        np.random.seed(seed_32bit)
        if hasattr(self.memory_manager, 'reset_memory_pool'):
            self.memory_manager.reset_memory_pool()

    def encrypt(self, key: str, salt: bytes, seed: int):
        try:
            # deterministik işlemlerin bu seedde olmasi gerekiyor daha sonra belki değişiklik yapabilirim şimdilik böyle birakiyorum.
            self._set_rng_seed(seed)

            key_matrices = self.key_scheduler.generate_key_matrices(key, salt, self.matrix_size)

            initialized_memory_blocks = self.memory_manager.initialize_blocks() 

            encrypted_matrices = self.matrix_handler.perform_hybrid_operations(key_matrices, self.iterations)

            raw_hash_parts = []
            for matrix in encrypted_matrices:
                matrix_normalized = np.abs(matrix) % 256
                raw_hash_parts.append(''.join(f"{int(val):02x}" for val in matrix_normalized.flatten()))

            raw_hash = "".join(raw_hash_parts)

            hash_b64 = base64.b64encode(raw_hash.encode('utf-8')).decode('utf-8')

            mod_bases_str = ":".join(map(str, self.mod_bases))
            param_str = f"m={self.memory_size},it={self.iterations},ms={self.matrix_size},mb={mod_bases_str}"

            seed_bytes = seed.to_bytes(8, 'big')
            seed_b64 = base64.b64encode(seed_bytes).decode('utf-8')
            salt_b64 = base64.b64encode(salt).decode('utf-8')

            final_str = f"$ozhash$v=1${param_str}${seed_b64}${salt_b64}${hash_b64}"
            return final_str

        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}")

    def verify(self, key: str, encoded_hash: str):
        try:
            parts = encoded_hash.split('$')
            if len(parts) != 7:
                raise VerificationError("Geçersiz hash formatı: Bölüm sayısı eşleşmiyor.")

            if parts[1] != 'ozhash':
                raise VerificationError("Geçersiz şema: 'ozhash' bekleniyordu.")
            if parts[2] != 'v=1':
                raise VerificationError("Geçersiz versiyon: 'v=1' bekleniyordu.")

            param_str = parts[3]
            seed_b64 = parts[4]
            salt_b64 = parts[5]
            hash_b64 = parts[6]
            params = {}
            for p in param_str.split(','):
                k, v = p.split('=')
                params[k] = v

            memory_size = int(params['m'])
            iterations = int(params['it'])
            matrix_size = int(params['ms'])
            mod_bases = list(map(int, params['mb'].split(':')))

            seed_bytes = base64.b64decode(seed_b64)
            if len(seed_bytes) != 8:
                raise VerificationError("Geçersiz seed uzunluğu: 8 bayt bekleniyordu.")
            seed = int.from_bytes(seed_bytes, 'big')

            salt = base64.b64decode(salt_b64)
            original_hash = base64.b64decode(hash_b64).decode('utf-8')

            temp_config = {
                "matrix_size": matrix_size,
                "memory_blocks": self.memory_blocks_count,
                "iterations": iterations,
                "mod_bases": mod_bases,
                "memory_size": memory_size,
                "process_mode": self.process_mode
            }

            temp_ozhash = OzHash(temp_config)

            re_encoded = temp_ozhash.encrypt(key, salt, seed)

            reparts = re_encoded.split('$')
            if len(reparts) != 7:
                raise VerificationError("Geçersiz yeniden kodlanmış hash formatı.")
            re_hash_b64 = reparts[6]
            re_original_hash = base64.b64decode(re_hash_b64).decode('utf-8')

            return re_original_hash == original_hash

        except Exception as e:
            raise VerificationError(f"Doğrulama başarısız oldu: {e}")

if __name__ == "__main__":
    config = {
        "matrix_size": 8,
        "memory_blocks": 4,
        "iterations": 12,
        "mod_bases": [353, 509, 613],
        "memory_size": 2048,
        "process_mode": "adaptive"
    }
