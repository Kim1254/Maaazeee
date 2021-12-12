#if !defined _ENCODER_INCLUDED
#define _ENCODER_INCLUDED

// pir char long long :)
using pcll = std::pair<char, long long>;

// A tree node with two children.
// Chiledren uses unique pointer to prevent them from duplication. only assign and move will be used.
typedef struct node_s {
	node_s(std::unique_ptr<struct node_s>& left, pcll& value, std::unique_ptr<struct node_s>& right)
	{
		this->left = std::move(left);
		this->value = value;
		this->right = std::move(right);
	};

	node_s(pcll& value)
	{
		this->left = nullptr;
		this->value = value;
		this->right = nullptr;
	};

	~node_s()
	{
		if (this->left != nullptr)
			this->left.reset();
		if (this->right != nullptr)
			this->left.reset();
	};

	std::unique_ptr<struct node_s> left;
	pcll value;
	std::unique_ptr<struct node_s> right;
} node_t;

// A Huffman function encodes multiple files into one package (second parameter.)
// Returns unique pointer of huffman tree's root node.
// Returns nullptr if there is an error.
std::unique_ptr<node_t> Huffman(std::vector<std::string>&, std::string);

#endif