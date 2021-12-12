#include "decode.h"

#include <tuple>

#pragma warning(disable: 6031)

using namespace std;

// TODO: Read 4 character and convert it as long.
long ReadLong(const char* buf)
{
	union swap {
		char c[4];
		long l;
	} temp;

	memcpy(temp.c, buf, 4);
	return temp.l;
}

// TODO: Read 8 character and convert it as double long.
long long ReadDoubleLong(const char* buf)
{
	union swap {
		char c[8];
		long long ll;
	} temp;
	memcpy(temp.c, buf, 8);
	return temp.ll;
}

// TODO: Make a huffman tree, same as one of encode.cpp
shared_ptr<node_t> Make_HuffmanTree(const char* buf, unsigned int length)
{
	pcll value;
	vector<shared_ptr<node_t>> list;

	for (int i = 0; i < length; i++)
	{
		value.first = *buf;
		buf++;

		value.second = ReadDoubleLong(buf);
		buf += 8;

		list.push_back(make_shared<node_t>(value));
	}

	shared_ptr<node_t> head = nullptr;

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

		auto fptr = *fmin;
		auto sptr = *smin;

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
		list.push_back(make_shared<node_t>(fptr, value, sptr));
	}

	head = *list.begin();

	return head;
}

void RemoveFolder(string& path)
{
	_finddata_t fd;

	auto handle = _findfirst((path + "\\*.*").c_str(), &fd);

	for (auto result = handle; result != -1; result = _findnext(handle, &fd))
	{
		if (!strncmp(fd.name, ".", 2) || !strncmp(fd.name, "..", 2))
			continue;

		string temp = (path + '\\') + fd.name;
		if (fd.attrib == _A_SUBDIR)
		{
			RemoveFolder(temp);
			continue;
		}
		filesystem::remove(temp.c_str());
	}

	_findclose(handle);

	filesystem::remove(path.c_str());
}

// TODO: Write decoded texts with encoded text and huffman tree's root node.
bool WriteFile(string& name, shared_ptr<node_t>& head, unique_ptr<bool[]>& huffman_str, int length)
{
	if (!head)
		return true;

	// Make sub directories.
	int index;
	const char* p = name.c_str();
	const char* q = strchr(p, '\\');

	while (q)
	{
		index = q - name.c_str();
		_mkdir((name.substr(0, index)).c_str());

		p = q;
		q = strchr(p + 1, '\\');
	}

	ofstream fout;
	try {
		fout.open(name, ios::out | ios::binary);
	}
	catch (...) {
		cout << "Failed open file:" << name << endl;
		return true;
	}

	auto node = head;
	shared_ptr<node_t> nextnode;

	for (int i = 0; i < length; i++)
	{
		nextnode = (!huffman_str[i]) ? node->left : node->right; // left: 0, right: 1

		if (!nextnode->left) // leaf node: write
		{
			fout.put(nextnode->value.first);
			node = head;
		}
		else
			node = nextnode;
	}
	fout.close();
	return false;
}

vector<string> Parse(const char* filepath)
{
	vector<string> result; // result: saves unpacked file list.

	ifstream fin;
	uintmax_t file_size;

	try {
		fin.open(filepath, ifstream::binary); // open
		file_size = filesystem::file_size(filepath);
	}
	catch (...) {
		cout << "Failed open file: " << filepath << endl;
		return result;
	};

	auto buf = make_unique<char[]>(file_size);

	fin.read(buf.get(), file_size); // read

	// We uses buffer pointer to parse data header.
	// After we read, we adds the size of data we read.
	auto reader = buf.get();

	if (strncmp(reader, ".HUFFMAN", 8)) // Confirm this package is huffman encoded package.
	{
		cout << "Error: this package is not huffman compressed one." << endl;
		fin.close();
		return result;
	}
	reader += 8;

	auto length = ReadLong(reader); // Size of leaf nodes in huffman tree
	reader += 4;

	auto head = Make_HuffmanTree(reader, length);
	reader += 9 * length; // sizeof(char) + sizeof(long long)

	length = ReadLong(reader); // The number of compressed files.
	reader += 4;

	vector<tuple<string, long, long>> list; // a tuple vector container saves file name, offset, and real length

	list.reserve(length);
	result.reserve(length);

	long offset, size;
	for (int i = 0; i < length; i++)
	{
		string name = reader; // split context with end of string: '\000'
		reader += name.size() + 1;

		offset = ReadLong(reader);
		reader += 4;

		size = ReadLong(reader);
		reader += 4;

		result.push_back(name);
		list.emplace_back(name, offset, size);
	}

	string path = g_strPath + "\\data";
	if (_access(path.c_str(), 0) != -1) // remove the sub directories if there are already existing files. (collusion prevent)
		RemoveFolder(path);

	// make data folder and set it as working directory.
	_mkdir(path.c_str());
	_chdir(path.c_str());

	for (auto iter = list.begin(); iter != list.end(); ++iter)
	{
		cout << "Write(" << distance(list.begin(), iter) + 1 << "/" << list.size() << "): " << get<0>(*iter) << endl;
		if (iter + 1 == list.end())
			length = 0; // we won't calc the last size since it is eof.
		else
			length = get<1>(*(iter + 1)) - get<1>(*iter); // ..else the length of compressed data is (next offset - current offset).

		auto bits = make_unique<bool[]>(8 * length); // bits using: 8 * compressed data size
		memset(bits.get(), false, 8 * length);

		for (int i = 0; i < length; i++)
		{
			for (int j = 0; j < 8; j++)
			{
				if (reader[i] & (1 << j))
					bits[i * 8 + j] = true;
			}
		}

		WriteFile(get<0>(*iter), head, bits, get<2>(*iter));
		cout << "Complete." << endl;
		reader += length;
		bits.reset();
	}
	buf.reset();

	fin.close();
	cout << "Decode ends." << endl;

	return result;
}