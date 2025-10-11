# Node class represents each element in the linked list
class Node:
    def __init__(self, data):
        self.data = data  # The value stored in the node
        self.next = None  # Pointer to the next node in the list

# LinkedList class contains the head of the list and methods to manipulate it
class LinkedList:
    def __init__(self):
        self.head = None # The starting point of the list

    # Method to add a new node to the end of the list
    def append(self, data):
        new_node = Node(data)
        # If the list is empty, the new node becomes the head
        if not self.head:
            self.head = new_node
            return
        # Otherwise, traverse to the end of the list and add the new node
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    # Method to print the entire linked list for visualization
    def print_list(self):
        current_node = self.head
        nodes = []
        while current_node:
            nodes.append(str(current_node.data))
            current_node = current_node.next
        print(" -> ".join(nodes))

    # Method to find the middle node of the linked list
    def find_middle(self):
        """
        Finds the middle element of the linked list using the slow and fast pointer approach.
        """
        if not self.head:
            print("The list is empty.")
            return None

        slow_pointer = self.head
        fast_pointer = self.head

        # Traverse the list until the fast pointer reaches the end
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next

        # At this point, the slow pointer is at the middle node
        return slow_pointer

# --- Main Execution Block ---
# This part of the code will run when you execute the script.
if __name__ == "__main__":
    
    # --- Test Case 1: Odd Number of Elements ---
    print("--- Test Case 1: Odd List ---")
    ll_odd = LinkedList()
    for i in range(1, 6):
        ll_odd.append(i) # Creates 1 -> 2 -> 3 -> 4 -> 5

    print("Input List:")
    ll_odd.print_list()
    middle_node_odd = ll_odd.find_middle()
    if middle_node_odd:
        print(f"The middle element is: {middle_node_odd.data}\n") # Expected: 3

    # --- Test Case 2: Even Number of Elements ---
    print("--- Test Case 2: Even List ---")
    ll_even = LinkedList()
    for i in range(1, 7):
        ll_even.append(i) # Creates 1 -> 2 -> 3 -> 4 -> 5 -> 6

    print("Input List:")
    ll_even.print_list()
    middle_node_even = ll_even.find_middle()
    if middle_node_even:
        print(f"The middle element is: {middle_node_even.data}\n") # Expected: 4

    # --- Edge Case 3: Empty List ---
    print("--- Edge Case 3: Empty List ---")
    ll_empty = LinkedList()
    print("Input List: (empty)")
    middle_node_empty = ll_empty.find_middle() # Expected: "The list is empty."
    if not middle_node_empty:
        print("Correctly handled empty list.\n")

    # --- Edge Case 4: Single Node List ---
    print("--- Edge Case 4: Single Node List ---")
    ll_single = LinkedList()
    ll_single.append(42) # Creates 42

    print("Input List:")
    ll_single.print_list()
    middle_node_single = ll_single.find_middle()
    if middle_node_single:
        print(f"The middle element is: {middle_node_single.data}\n") # Expected: 42
