#pragma once

#include <iostream>
#include <string>
#include <vector>

#include <chrono>
#include <fstream>
#include <filesystem>
#include <algorithm>

using pcll = std::pair<char, long long>;

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

void Parse(const char* filepath);
