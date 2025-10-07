class DSU:
    """
    Disjoint Set Union data structure with path compression and union by rank.
    Supports efficient set operations in near-constant amortized time.
    """
    
    def __init__(self, n):
        """
        Initialize DSU with n elements (0 to n-1).
        
        Args:
            n: Number of elements
        """
        self.parent = list(range(n))
        self.rank = [0] * n
        self.size = [1] * n
    
    def find(self, x):
        """
        Find representative of set containing x with path compression.
        
        Args:
            x: Element to find
            
        Returns:
            Root of the set containing x
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """
        Merge sets containing x and y using union by rank.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if sets were merged, False if already in same set
        """
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        self.size[px] += self.size[py]
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
    
    def connected(self, x, y):
        """
        Check if x and y are in the same set.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if in same set, False otherwise
        """
        return self.find(x) == self.find(y)
    
    def get_size(self, x):
        """
        Get size of set containing x.
        
        Args:
            x: Element to query
            
        Returns:
            Number of elements in the set
        """
        return self.size[self.find(x)]
