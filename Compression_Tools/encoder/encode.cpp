#include "base.h"

#pragma warning(disable: 6031)

using namespace std;
using namespace chrono_literals;

using table = unordered_map<char, long long>;
using cstrmap = unordered_map<char, string>;

void Make_HuffmanTree(cstrmap& map, unique_ptr<node_t>& node, string str)
{
	if (node == nullptr)
		return;

	if (node->left == nullptr)
		map.insert(cstrmap::value_type(node->value.first, str));
	else
	{
		Make_HuffmanTree(map, node->left, str + "0");
		Make_HuffmanTree(map, node->right, str + "1");
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

void Write_Huffman(ofstream& file, unique_ptr<node_t>& node)
{
	if (node == nullptr)
		return;

	file << node->value.first;
	union swapping {
		long long value;
		char c[8];
	} temp;

	temp.value = node->value.second;
	file.write(temp.c, 8);

	Write_Huffman(file, node->left);
	Write_Huffman(file, node->left);
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
	counter.reserve(map.size());

	pcll value;
	for (auto iter = map.begin(); iter != map.end(); ++iter)
	{
		value = make_pair(iter->first, iter->second);
		counter.push_back(make_unique<node_t>(value));
	}

	sort(counter.begin(), counter.end(),
		[](unique_ptr<node_t>& a, unique_ptr<node_t>& b) -> bool {
		return a->value.second < b->value.second;
	});

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

		if (fmin > smin)
		{
			if (distance(counter.begin(), fmin) != counter.size() - 1)
				iter_swap(counter.end() - 1, fmin);
			counter.pop_back();

			if (distance(counter.begin(), smin) != counter.size() - 1)
				iter_swap(counter.end() - 1, smin);
			counter.pop_back();
		}
		else
		{
			if (distance(counter.begin(), smin) != counter.size() - 1)
				iter_swap(counter.end() - 1, smin);
			counter.pop_back();

			if (distance(counter.begin(), fmin) != counter.size() - 1)
				iter_swap(counter.end() - 1, fmin);
			counter.pop_back();
		}

		value = make_pair(0, fptr->value.second + sptr->value.second);
		counter.push_back(make_unique<node_t>(fptr, value, sptr));
	}

	auto head = move(counter.front());
	cout << "Tree construction complete. (Total " << TreeSize(head) << " nodes)" << endl;

	cstrmap char_map;
	Make_HuffmanTree(char_map, head, "");

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
	Write_Huffman(fout, head);

	function write_task = [&char_map](const char* buf, vector<bool>& wbuf, unsigned long long i, int length) {
		string str = "";
		table::iterator iter;
		for (unsigned long long i = 0; i < length; i++)
			str += char_map.at(buf[i]);

		for (int i = 0; i < str.size(); i++)
			wbuf.push_back((str[i] - '0') ? true : false);
	};

	i = 0;
	string output_name = "";
	string output_context = "";

	vector<bool> name;
	vector<vector<bool>> sub_buffer;

	char c;

	for (auto& file : file_list)
	{
		try {
			cout << "Write(" << ++i << "/" << file_list.size() << "): " << file.c_str() << endl;

			fin.open(file.c_str(), ios::binary);

			output_name += file;
			for (int i = 0; i < 4; i++)
			{
				c = 0;
				for (int j = 0; j < 8; j++)
					if ((1 << (i * 8 + j)) & output_context.size())
						c |= (1 << (8 - j));
				output_name.push_back(c);
			};

			auto file_size = filesystem::file_size(file);
			auto buf = make_unique<char[]>(file_size);

			fin.read(buf.get(), file_size);

			int sub_buf_size = file_size / length;
			if (file_size % length)
				sub_buf_size++;

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
					c = 0;

					for (int j = i; j < iMin; j++)
					{
						if (sub[j] == true)
							c |= (1 << (8 - j - i));
					}
					output_context.push_back(c);
				}
				vector<bool>().swap(sub);
			}
			vector<vector<bool>>().swap(sub_buffer);

			buf.reset();
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	fout.write(output_name.c_str(), output_name.size());
	fout.write(output_context.c_str(), output_context.size());

	vector<unique_ptr<node_t>>().swap(counter);
	vector<bool>().swap(name);
	vector<future<void>>().swap(threads);
	vector<future<void>>().swap(sub_threads);

	fout.close();
	cout << "Write ends." << endl;

	return head;
}