#if !defined _ENCODER_INCLUDED
#define _ENCODER_INCLUDED

using pcll = std::pair<char, long long>;

typedef struct node_s {
	struct node_s(std::unique_ptr<struct node_s>& left, pcll& value, std::unique_ptr<struct node_s>& right)
	{
		this->left = std::move(left);
		this->value = value;
		this->right = std::move(right);
	};

	struct node_s(pcll& value)
	{
		this->left = nullptr;
		this->value = value;
		this->right = nullptr;
	};

	std::unique_ptr<struct node_s> left;
	pcll value;
	std::unique_ptr<struct node_s> right;
} node_t;

std::unique_ptr<node_t> Huffman(std::vector<std::string>&);

#endif