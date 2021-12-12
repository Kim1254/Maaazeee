#include "base.h"
#include "decode.h"

#pragma warning(disable: 6031)

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

shared_ptr<snode_t> Make_HuffmanTree(const char* buf, unsigned int length)
{
	pcll value;
	vector<shared_ptr<snode_t>> list;

	for (int i = 0; i < length; i++)
	{
		value.first = *buf;
		buf++;

		value.second = ReadDoubleLong(buf);
		buf += 8;

		list.push_back(make_shared<snode_t>(value));
	}

	shared_ptr<snode_t> head = nullptr;

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
		list.push_back(make_shared<snode_t>(fptr, value, sptr));
	}

	head = *list.begin();

	list.clear();

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

bool WriteFile(string& name, shared_ptr<snode_t> head, unique_ptr<bool[]>& huffman_str, int length)
{
	int index;
	const char* p = name.c_str();
	const char* q = strchr(p, '\\');

	while (q)
	{
		index = q - name.c_str();
		_mkdir(name.substr(0, index).c_str());

		p = q;
		q = strchr(p + 1, '\\');
	}

	ofstream fout;
	try {
		fout.open(name, ios_base::binary);
	}
	catch (...) {
		cout << "Failed open file:" << name << endl;
		return true;
	}

	shared_ptr<snode_t> node = head;

	string text;

	for (int i = 0; i < length; i++)
	{
		if (node->left == nullptr)
		{
			fout.put(node->value.first);
			node = head;
		}

		if (!huffman_str[i])
			node = node->left;
		else
			node = node->right;
	}
	fout.close();
	return false;
}

void Parse(const char* filepath)
{
	ifstream fin;
	uintmax_t file_size;

	try {
		fin.open(filepath, ios_base::binary);
		file_size = filesystem::file_size(filepath);
	}
	catch (...) {
		cout << "Failed open file: " << filepath << endl;
		return;
	};

	auto buf = make_unique<char[]>(file_size);

	fin.read(buf.get(), file_size);

	auto reader = buf.get();

	if (strncmp(reader, ".HUFFMAN", 8))
	{
		cout << "Error: this package is not huffman compressed one." << endl;
		fin.close();
		return;
	}
	reader += 8;

	auto length = ReadLong(reader); // Size of leaf nodes in huffman tree
	reader += 4;

	auto head = Make_HuffmanTree(reader, length);
	reader += 9 * length; // sizeof(char) + sizeof(long long)

	length = ReadLong(reader);
	reader += 4;

	vector<pair<string, long>> list;
	list.reserve(length);

	cout << "len: " << length << endl;
	for (int i = 0; i < length; i++)
	{
		string name = reader; // split context with end of string: '\000'
		reader += name.size() + 1;
		auto offset = ReadLong(reader);
		reader += 4;
		list.emplace_back(name, offset);
	}

	string path = g_strPath + "\\output";
	if (_access(path.c_str(), 0) != -1)
		RemoveFolder(path);

	_mkdir(".\\output");

	for (auto iter = list.begin(); iter != list.end(); ++iter)
	{
		if (iter + 1 == list.end())
			length = file_size - (reader - buf.get());
		else
			length = (iter + 1)->second - iter->second;

		int counter = 0;
		auto bits = make_unique<bool[]>(8 * length);
		memset(bits.get(), false, 8 * length);

		for (int i = 0; i < length; i++)
		{
			for (int j = 0; j < 8; j++)
				if (reader[i] & (1 << j))
					bits[i * 8 + j] = true;
		}

		WriteFile(iter->first, head, bits, length);
		reader += length;
	}

	fin.close();
}