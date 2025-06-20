import numpy as np
import math

class MatrixHandler:
    def __init__(self, matrix_size, mod_bases, memory_size=1024, memory_manager=None):
        self.matrix_size = matrix_size
        self.mod_bases = mod_bases
        self.memory_size = memory_size
        
        # Dışarıdan bir MemoryBlocks örneği al
        if memory_manager is None:
            raise ValueError("MatrixHandler requires a MemoryBlocks instance.")
        self.memory_manager = memory_manager 

    def perform_data_independent_operations(self, matrices, iterations):
        """Veriden bağımsız bellek erişim işlemlerini deterministik olarak gerçekleştirir."""
        for iteration in range(iterations):
            for idx, matrix in enumerate(matrices):
                mod_base = self.mod_bases[(iteration + idx) % len(self.mod_bases)]
                # Bellek erişimi için MemoryBlocks örneğini kullan
                for i in range(self.matrix_size):
                    for j in range(self.matrix_size):
                        memory_value = self.memory_manager.get_main_memory_pool_value(i, j)
                        # Veri tipini tutarlı tut
                        matrix[i, j] = int((int(matrix[i, j]) + memory_value) % mod_base)
                matrices[idx] = matrix
        return matrices

    def perform_data_dependent_operations(self, matrices, iterations):
        """Veriye bağımlı bellek erişim işlemlerini deterministik olarak gerçekleştirir."""
        for iteration in range(iterations):
            for idx, matrix in enumerate(matrices):
                mod_base = self.mod_bases[(iteration + idx) % len(self.mod_bases)]
                # Bellek erişimi için MemoryBlocks örneğini kullan
                for i in range(self.matrix_size):
                    for j in range(self.matrix_size):
                        # Güvenli indeks hesaplama
                        matrix_val = int(abs(matrix[i, j]))
                        dependent_index = matrix_val % self.memory_size
                        
                        memory_value = self.memory_manager.get_main_memory_pool_value(i, dependent_index)
                        # Veri tipini tutarlı tut
                        matrix[i, j] = int((matrix_val + memory_value) % mod_base)
                matrices[idx] = matrix
        return matrices

    def perform_hybrid_operations(self, matrices, iterations):
        """Hibrit (veriye bağımlı ve bağımsız) işlemleri deterministik olarak gerçekleştirir."""
        for iteration in range(iterations):
            for idx, matrix in enumerate(matrices):
                mod_base = self.mod_bases[(iteration + idx) % len(self.mod_bases)]
                
                try:
                    if matrix.dtype != np.int32:
                        matrix = matrix.astype(np.int32)
                    
                    if iteration % 2 == 0: 
                        for i in range(self.matrix_size):
                            for j in range(self.matrix_size):
                                memory_value = self.memory_manager.get_main_memory_pool_value(i, j)
                                matrix[i, j] = int((int(matrix[i, j]) + memory_value) % mod_base)
                    else:
                        for i in range(self.matrix_size):
                            for j in range(self.matrix_size):
                                matrix_val = int(abs(matrix[i, j]))
                                dependent_index = matrix_val % self.memory_size
                                
                                memory_value = self.memory_manager.get_main_memory_pool_value(i, dependent_index)
                                matrix[i, j] = int((matrix_val + memory_value) % mod_base)

                    if not isinstance(matrix, np.ndarray):
                        raise ValueError(f"Matrix {idx} is not a numpy array.")
                    
                    matrix = matrix.astype(np.int32)
                    matrices[idx] = matrix
                    
                except Exception as e:
                    raise ValueError(f"Hata: Matris {idx} ({iteration}. iterasyonda) işlenirken hata oluştu: {e}")
        return matrices

    def flatten_matrices(self, matrices):
        flattened_parts = []
        for matrix in matrices:
            matrix_int = matrix.astype(np.int32)
            matrix_normalized = np.abs(matrix_int) % 256
            hex_values = [f"{int(val):02x}" for val in matrix_normalized.flatten()]
            flattened_parts.append(''.join(hex_values))
        
        return ''.join(flattened_parts)