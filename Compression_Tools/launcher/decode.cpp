#include "decode.h"

using namespace std;

long ReadLong(const char* buf)
{
	union swap {
		char c[4];
		long l;
	} temp;

	memcpy(temp.c, buf, 4);
	return temp.l;
}

long long ReadDoubleLong(const char* buf)
{
	union swap {
		char c[8];
		long long ll;
	} temp;
	memcpy(temp.c, buf, 8);
	return temp.ll;
}

unique_ptr<node_t> Make_HuffmanTree(const char* buf, unsigned int length)
{
	pcll value;
	vector<unique_ptr<node_t>> list;

	for (int i = 0; i < length; i++)
	{
		value.first = *buf;
		buf++;

		value.second = ReadDoubleLong(buf);
		buf += 8;

		list.push_back(make_unique<node_t>(value));
	}

	unique_ptr<node_t> head = nullptr;

	while (list.size() != 1)
	{
		auto fmin = list.end();
		auto smin = list.end();

		for (auto iter = list.begin(); iter != list.end(); ++iter)
		{
			if (fmin == list.end())
			{
				fmin = iter;
				continue;
			}

			if (smin == list.end())
			{
				smin = iter;
				continue;
			}

			if ((*fmin)->value.second > (*iter)->value.second)
				fmin = iter;
			else if ((*smin)->value.second > (*iter)->value.second)
				smin = iter;
		}

		if (fmin == list.end() || smin == list.end())
			return nullptr;

		auto fptr = move(*fmin);
		auto sptr = move(*smin);

		if (fmin > smin)
		{
			if (distance(list.begin(), fmin) != list.size() - 1)
				iter_swap(list.end() - 1, fmin);
			list.pop_back();

			if (distance(list.begin(), smin) != list.size() - 1)
				iter_swap(list.end() - 1, smin);
			list.pop_back();
		}
		else
		{
			if (distance(list.begin(), smin) != list.size() - 1)
				iter_swap(list.end() - 1, smin);
			list.pop_back();

			if (distance(list.begin(), fmin) != list.size() - 1)
				iter_swap(list.end() - 1, fmin);
			list.pop_back();
		}

		value = make_pair(0, fptr->value.second + sptr->value.second);
		list.push_back(make_unique<node_t>(fptr, value, sptr));
	}

	head = move(*list.begin());

	return head;
}

void Parse(const char* filepath)
{
	fstream fin;
	try {
		fin.open(filepath, ios_base::binary);
	}
	catch (...) {
		cout << "Failed open file: " << filepath << endl;
		return;
	};

	auto file_size = filesystem::file_size(filepath);
	auto buf = make_unique<char[]>(file_size);

	fin.read(buf.get(), file_size);

	const auto csize = sizeof(char);
	const auto lsize = sizeof(long);
	const auto llsize = sizeof(long long);

	auto reader = buf.get();
	if (strncmp(reader, ".HUFFMAN", 8))
	{
		cout << "Error: this package is not huffman compressed one." << endl;
		return;
	}
	reader += csize * 8;

	auto length = ReadLong(reader); // Size of leaf nodes in huffman tree
	reader += lsize;

	auto head = Make_HuffmanTree(reader, length);
	reader += (csize + llsize) * length;

	length = ReadLong(reader);
	reader += lsize;

	vector<pair<string, long>> list;
	list.reserve(length);

	for (int i = 0; i < length; i++)
	{
		string str = reader;
		cout << str << ", " << str.size() << endl;
		break;
	}
}