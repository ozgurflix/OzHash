import numpy as np
import hashlib
import math

class KeyScheduler:
    def __init__(self, mod_bases, memory_size=1024, memory_manager=None):
        self.mod_bases = mod_bases
        self.memory_size = memory_size
        if memory_manager is None:
            raise ValueError("KeyScheduler requires a MemoryBlocks instance.")
        self.memory_manager = memory_manager 

    def generate_key_matrices(self, key, salt, matrix_size):
        combined = (key + salt.hex()).encode('utf-8')
        hash_value = hashlib.blake2b(combined, digest_size=64).digest()

        key_matrices = []
        for mod_base in self.mod_bases:
            matrix = np.zeros((matrix_size, matrix_size), dtype=np.int32)
            
            for i in range(matrix_size):
                for j in range(matrix_size):
                    index = (i * matrix_size + j) % len(hash_value)
                    
                    memory_value = self.memory_manager.get_main_memory_pool_value(i, j)
                    hash_val = int(hash_value[index])
                    position_val = (i * j) % mod_base
                    combined_val = (hash_val + position_val + memory_value) % mod_base
                    
                    matrix[i, j] = combined_val
            matrix = self.apply_transformations_sequential(matrix, mod_base)
            key_matrices.append(matrix)

        return key_matrices

    def apply_transformations_sequential(self, matrix, mod_base):
        transformed_matrix = np.zeros_like(matrix, dtype=np.int32)
        
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = int(matrix[i, j])
                safe_value = value % (mod_base // 2 + 1)
                
                try:
                    sin_val = math.sin(safe_value * math.pi / mod_base)
                    cos_val = math.cos(safe_value * math.pi / mod_base)
                    exp_val = math.exp(safe_value / mod_base) if safe_value / mod_base < 10 else 1.0
                    
                    normalized_result = (abs(sin_val) + abs(cos_val) + abs(exp_val)) / 3.0
                    transformed_value = int(normalized_result * mod_base) % mod_base
                    
                except (OverflowError, ValueError):
                    transformed_value = (value * 31 + 17) % mod_base
                
                transformed_matrix[i, j] = transformed_value
                
        return transformed_matrix

    def normalize_matrix(self, matrix, mod_base):
        normalized = matrix.astype(np.int32) % mod_base
        return normalized