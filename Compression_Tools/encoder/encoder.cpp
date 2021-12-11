#include <iostream>
#include <string>
#include <vector>
#include <bitset>

#include <future>
#include <thread>
#include <chrono>
#include <mutex>

#include <fstream>
#include <filesystem>

#include <algorithm>
#include <functional>

#include <io.h>
#include <direct.h>

#pragma warning(disable: 6031)

using namespace std;

using namespace chrono_literals;

using table = unordered_map<char, long long>;
using cstrmap = unordered_map<char, string>;
using pcll = pair<char, long long>;

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

void HuffmanTree(cstrmap& map, unique_ptr<node_t>& node, string str)
{
	if (node == nullptr)
		return;

	if (node->left == nullptr)
		map.insert(cstrmap::value_type(node->value.first, str));
	else
	{
		HuffmanTree(map, node->left, str + "0");
		HuffmanTree(map, node->right, str + "1");
	}
}

unsigned int TreeSize(unique_ptr<node_t>& node)
{
	if (node == nullptr)
		return 0;

	unsigned int size = 1;
	size += TreeSize(node->left);
	size += TreeSize(node->right);
	return size;
}

unique_ptr<node_t> Huffman(vector<string>& file_list)
{
	if (!file_list.size())
		return nullptr;

	table map;
	vector<future<void>> threads;

	mutex mtx;

	ifstream fin;

	int thread_running = 0;
	vector<future<void>> sub_threads;
	function read_task = [&map, &mtx](const char* buf, unsigned long long i, int length) {
		table::iterator iter;
		for (unsigned long long i = 0; i < length; i++)
		{
			mtx.lock();
			iter = map.find(buf[i]);
			if (iter == map.end())
				map.insert(table::value_type(buf[i], 1));
			else
				iter->second++;
			mtx.unlock();
		}
	};

	const unsigned long long length = 1000000;

	int i = 0;
	for (auto& file : file_list)
	{
		try {
			cout << "Read(" << ++i << "/" << file_list.size() << "): " << file.c_str() << endl;
			
			fin.open(file.c_str(), ios::binary);

			auto file_size = filesystem::file_size(file);
			auto buf = make_unique<char[]>(file_size);

			fin.read(buf.get(), file_size);

			for (unsigned long long i = 0; i < file_size; i += length)
			{
				do
				{
					thread_running = 0;
					for (auto& th : sub_threads)
					{
						if (th.wait_for(0ms) != future_status::ready)
							thread_running++;
					}
				} while (thread_running >= 10);
				sub_threads.push_back(async(launch::async, read_task, buf.get(), i, min(length, file_size - i)));
			}

			for (auto& th : sub_threads)
				while (th.wait_for(0ms) != future_status::ready); // join

			sub_threads.clear();

			buf.reset();
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	cout << "Waiting for threads..." << endl;

	for (auto& fu : threads)
		while (fu.wait_for(0ms) != future_status::ready); // join
	
	if (!map.size())
		return nullptr;

	vector<unique_ptr<node_t>> counter;

	pcll value;
	for (auto iter = map.begin(); iter != map.end(); ++iter)
	{
		value = pcll(iter->first, iter->second);
		counter.push_back(make_unique<node_t>(value));
	}

	sort(counter.begin(), counter.end(),
		[](unique_ptr<node_t>& a, unique_ptr<node_t>& b) -> bool {
		return a->value.second < b->value.second;
	});

	for (auto iter = counter.begin(); iter != counter.end(); ++iter)
	{
		cout << (int)(*iter)->value.first << ": " << (*iter)->value.second << endl;
	}

	cout << "Character count complete. (Total " << counter.size() << ")" << endl;

	while (counter.size() != 1)
	{
		auto fmin = counter.end();
		auto smin = counter.end();

		for (auto iter = counter.begin(); iter != counter.end(); ++iter)
		{
			if (fmin == counter.end())
			{
				fmin = iter;
				continue;
			}
			if (smin == counter.end())
			{
				smin = iter;
				continue;
			}

			if ((*fmin)->value.second > (*iter)->value.second)
				fmin = iter;
			else if ((*smin)->value.second > (*iter)->value.second)
				smin = iter;
		}

		if (fmin == counter.end() || smin == counter.end())
			return nullptr;

		auto fptr = move(*fmin);
		auto sptr = move(*smin);

		value = pcll(0, fptr->value.second + sptr->value.second);
		counter.push_back(make_unique<node_t>(fptr, value, sptr));

		if (fmin > smin)
		{
			counter.erase(fmin);
			counter.erase(smin);
		}
		else
		{
			counter.erase(smin);
			counter.erase(fmin);
		}
	}

	auto head = move(counter.front());
	cout << "Tree construction complete. (Total " << TreeSize(head) << " nodes)" << endl;

	cstrmap char_map;
	HuffmanTree(char_map, head, "");

	for (auto iter = char_map.begin(); iter != char_map.end(); ++iter)
		cout << (int)iter->first << ": " << iter->second << endl;
	cout << "Huffman tree construction complete. (Total " << char_map.size() << ")" << endl;

	ofstream fout;

	try {
		fout.open("data.pak", ios_base::binary);
	}
	catch (...) {
		cout << "Failed creating output file." << endl;
		return nullptr;
	}
	fout << ".HUFFMAN";

	function write_task = [&head, &char_map](const char* buf, vector<bool>& wbuf, unsigned long long i, int length) {
		string str = "";
		table::iterator iter;
		for (unsigned long long i = 0; i < length; i++)
			str += char_map.at(buf[i]);

		for (int i = 0; i < str.size(); i++)
			wbuf.push_back((str[i] - '0') ? true : false);
	};

	i = 0;

	for (auto& file : file_list)
	{
		try {
			cout << "Write(" << ++i << "/" << file_list.size() << "): " << file.c_str() << endl;

			fin.open(file.c_str(), ios::binary);

			auto file_size = filesystem::file_size(file);
			auto buf = make_unique<char[]>(file_size);

			fin.read(buf.get(), file_size);

			int sub_buf_size = file_size / length;
			if (file_size % length)
				sub_buf_size++;

			vector<vector<bool>> sub_buffer;
			sub_buffer.reserve(sub_buf_size);

			for (unsigned long long i = 0; i < file_size; i += length)
			{
				do
				{
					thread_running = 0;
					for (auto& th : sub_threads)
					{
						if (th.wait_for(0ms) != future_status::ready)
							thread_running++;
					}
				} while (thread_running >= 10);

				sub_buffer.push_back(vector<bool>());
				sub_threads.push_back(async(launch::async, write_task, buf.get(), ref(sub_buffer.back()), i, min(length, file_size - i)));
			}

			for (auto& th : sub_threads)
				while (th.wait_for(0ms) != future_status::ready); // join

			sub_threads.clear();

			for (auto& sub : sub_buffer)
			{
				for (int i = 0; i < sub.size(); i += 8)
				{
					int iMin = min(i + 8, (int)sub.size());
					char c = 0;

					for (int j = i; j < iMin; j++)
					{
						if (sub[j] == true)
							c |= (1 << (j - i));
					}
					fout << c;
				}
				sub.clear();
			}
			sub_buffer.clear();

			buf.reset();
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	fout.close();
	cout << "Write ends." << endl;

	return nullptr;
}

void SearchFiles(const char* path, vector<string>& list)
{
	string ppath = path;
	ppath += "\\*.*";

	_finddata_t fd;

	auto handle = _findfirst(ppath.c_str(), &fd);

	for (auto result = handle; result != -1; result = _findnext(handle, &fd))
	{
		if (!strncmp(fd.name, ".", 2) || !strncmp(fd.name, "..", 2))
			continue;

		if (fd.attrib == _A_SUBDIR)
		{
			SearchFiles((ppath.substr(0, ppath.length() - 3) + fd.name).c_str(), list);
			continue;
		}

		list.push_back(ppath.substr(0, ppath.length() - 3) + fd.name);
	}

	_findclose(handle);
}

int main(int argc, char* argv[])
{
	if (argc != 2)
		return 1;

	string target = argv[1];

	vector<string> file_list;
	SearchFiles(target.c_str(), file_list);

	auto cut = target.length() + 1; // \\

	for (auto iter = file_list.begin(); iter != file_list.end(); ++iter)
	{
		*iter = iter->substr(cut, iter->length());
		//cout << *iter << endl;
	}

	_chdir(argv[1]);

	Huffman(file_list);
	system("pause>nul");

	return 1;
}