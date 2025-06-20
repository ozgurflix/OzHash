import numpy as np

class MemoryBlocks:
    def __init__(self, num_blocks, matrix_size, mod_bases, memory_size=1024):
        self.num_blocks = num_blocks
        self.matrix_size = matrix_size
        self.mod_bases = mod_bases
        self.memory_size = memory_size
        self._main_memory_pool = None 
        
        self.memory_blocks = [] 

    def _initialize_main_memory_pool(self):
        if self._main_memory_pool is None:
            self._main_memory_pool = np.array([
                np.random.randint(0, 256, self.memory_size, dtype=np.int32)
                for _ in range(len(self.mod_bases))
            ])
        return self._main_memory_pool

    def get_main_memory_pool_value(self, i, j):
        if self._main_memory_pool is None:
            self._initialize_main_memory_pool()
        
        block_idx = abs(i) % len(self.mod_bases)
        element_idx = abs(i * j) % self.memory_size
        
        return int(self._main_memory_pool[block_idx, element_idx])

    def generate_block(self, mod_base):
        if self._main_memory_pool is None:
            self._initialize_main_memory_pool()
        

        block = np.random.randint(0, mod_base, (self.matrix_size, self.matrix_size), dtype=np.int32)

        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                memory_value = self.get_main_memory_pool_value(i, j)
                current_val = int(block[i, j])
                squared_val = (current_val * current_val) % mod_base
                combined_val = (squared_val + memory_value) % mod_base
                block[i, j] = combined_val // 2 if combined_val >= 2 else combined_val
                
        return block

    def initialize_blocks(self):
        if self._main_memory_pool is None:
            self._initialize_main_memory_pool()
            
        self.memory_blocks = [] # Her çağrıda sıfırla
        for mod_base in self.mod_bases:
            blocks_for_mod = [
                self.generate_block(mod_base) for _ in range(self.num_blocks)
            ]
            self.memory_blocks.extend(blocks_for_mod)
        return self.memory_blocks

    def reset_memory_pool(self):
        self._main_memory_pool = None
        self.memory_blocks = []