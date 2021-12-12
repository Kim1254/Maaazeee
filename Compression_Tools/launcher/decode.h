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

using pcll = std::pair<char, long long>;

typedef struct snode_s {
	snode_s(std::shared_ptr<struct snode_s>& left, pcll& value, std::shared_ptr<struct snode_s>& right)
	{
		this->left = left;
		this->value = value;
		this->right = right;
	};

	snode_s(pcll& value)
	{
		this->left = nullptr;
		this->value = value;
		this->right = nullptr;
	};

	void operator=(const struct snode_s& other)
	{
		this->left = other.left;
		this->value = other.value;
		this->right = other.right;
	};

	std::shared_ptr<struct snode_s> left;
	pcll value;
	std::shared_ptr<struct snode_s> right;
} snode_t;

std::vector<std::string> Parse(const char* filepath);
void RemoveFolder(std::string& path);
