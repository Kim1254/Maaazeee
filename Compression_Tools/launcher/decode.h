#pragma once

#include <iostream>
#include <string>
#include <vector>

#include <chrono>
#include <fstream>
#include <filesystem>
#include <algorithm>

#include <io.h>
#include <direct.h>

extern std::string g_strPath;

// pir char long long :)
using pcll = std::pair<char, long long>;

// A tree node with two children.
// Chiledren uses shared pointer since the huffman tree called for many times.(and many copies and references.)
typedef struct node_s {
	node_s(std::shared_ptr<struct node_s>& left, pcll& value, std::shared_ptr<struct node_s>& right)
	{
		this->left = left;
		this->value = value;
		this->right = right;
	};

	node_s(pcll& value)
	{
		this->left = nullptr;
		this->value = value;
		this->right = nullptr;
	};

	void operator=(const struct node_s& other)
	{
		this->left = other.left;
		this->value = other.value;
		this->right = other.right;
	};

	std::shared_ptr<struct node_s> left;
	pcll value;
	std::shared_ptr<struct node_s> right;
} node_t;

// TODO: Parse(Unpack) package
std::vector<std::string> Parse(const char*);

// TODO: Remove the folder and all files and folders in this folder.
void RemoveFolder(std::string&);
