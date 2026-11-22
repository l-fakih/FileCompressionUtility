// 1. Define a "Node" in the Huffman Tree
struct Node {
    char data;
    unsigned freq;// How many times it appears in the file
    Node *left, *right; // Pointers to child nodes to build the tree branches
};

// 2. Step One: Frequency Analysis
void calculateFrequencies(string filename) {
    // Open the file using a file stream
    // Read the file character by character
    // Use an array or hash map (like int freq[256] = {0})
    // For every char 'c' read, do: freq[c]++;
}

// 3. Step Two: Build the Tree
void buildHuffmanTree() {
    // Create a Priority Queue (a min-heap) to store all nodes.
    // Insert all characters with a frequency > 0 into the queue.
    // Loop while there is more than 1 node in the queue:
        // Extract the two nodes with the LOWEST frequencies.
        // Create a new parent node. Its frequency is the sum of the two children.
        // Make the two extracted nodes the left and right children of this parent.
        // Push the new parent node back into the priority queue.
    // The last remaining node in the queue is the Root of your Huffman Tree!
}

// 4. Step Three: Generate Codes
void generateCodes(Node* root, string currentCode) {
    // Recursively walk down the tree.
    // If you go left, append '0' to currentCode.
    // If you go right, append '1' to currentCode.
    // If you reach a leaf node (a character), save currentCode to a map.
}

// 5. Step Four: Compress
void compressFile() {
    // Read the original file again.
    // Look up each character's binary string in your map.
    // Pack those '0's and '1's into actual bytes (8 bits = 1 byte) using bitwise operators (<<, |, etc.).
    // Write the resulting bytes to "compressed.bin".
    // IMPORTANT: You must also save the tree or frequency table in the file header so the decompressor knows how to read it!
}