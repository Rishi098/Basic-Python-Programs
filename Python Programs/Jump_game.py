class Solution:
    def canJump(self, nums):
        max_reachable = 0
        n = len(nums)

        for i in range(n):
            if i > max_reachable:
                return False
            max_reachable = max(max_reachable, nums[i] + i)

        return True

# TC = O(N)
# SC = O(1)
