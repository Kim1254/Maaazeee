#include "base.h"

#pragma warning(disable: 6031)

using namespace std;
using namespace chrono_literals;

using table = unordered_map<char, long long>;
using cstrmap = unordered_map<char, string>;

void Make_HuffmanMap(cstrmap& map, unique_ptr<node_t>& node, string str)
{
	if (node->left)
	{
		Make_HuffmanMap(map, node->left, str + "0");
		Make_HuffmanMap(map, node->right, str + "1");
	}
	else
		map.insert(cstrmap::value_type(node->value.first, str));
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

void WriteLong(ofstream& stream, long l)
{
	union swap {
		long l;
		char c[4];
	} temp;
	temp.l = l;

	stream.write(temp.c, 4);
}

void WriteDoubleLong(ofstream& stream, long long ll)
{
	union swap {
		long long ll;
		char c[8];
	} temp;
	temp.ll = ll;

	stream.write(temp.c, 8);
}

unique_ptr<node_t> Huffman(vector<string>& file_list, string output_file_name)
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

			fin.open(file.c_str(), ifstream::binary);

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
	Make_HuffmanMap(char_map, head, "");

	cout << "Huffman tree construction complete. (Total " << char_map.size() << ")" << endl;

	function write_task = [&char_map](const char* buf, vector<bool>& wbuf, unsigned long long i, int length) {
		string str = "";
		for (unsigned long long i = 0; i < length; i++)
			str += char_map.at(buf[i]);

		for (auto c : str)
			wbuf.push_back((c - '0') ? true : false);
	};

	i = 0;
	string output_name = "";
	string output_context = "";

	vector<bool> name;
	vector<vector<bool>> sub_buffer;

	function swritel = [](string& string, long l) {
		union swap {
			long l;
			char c[4];
		} temp;
		temp.l = l;

		for (int i = 0; i < 4; i++)
			string.push_back(temp.c[i]);
	};
	
	for (auto& file : file_list)
	{
		try {
			cout << "Write(" << ++i << "/" << file_list.size() << "): " << file.c_str() << endl;

			fin.open(file.c_str(), ifstream::binary);

			output_name += file;
			output_name.push_back('\0');
			swritel(output_name, output_context.size());

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

			int total_length = 0;
			for (auto& sub : sub_buffer)
			{
				total_length += sub.size();
				for (int i = 0; i < sub.size(); i += 32)
				{
					int iMin = min(i + 32, (int)sub.size());
					long l = 0;

					for (int j = i; j < iMin; j++)
					{
						if (sub[j] == true)
							l |= (1 << (j + i));
					}
					swritel(output_context, l);
				}
				vector<bool>().swap(sub);
			}
			swritel(output_name, total_length);
			vector<vector<bool>>().swap(sub_buffer);

			buf.reset();
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	vector<unique_ptr<node_t>>().swap(counter);
	vector<bool>().swap(name);
	vector<future<void>>().swap(threads);
	vector<future<void>>().swap(sub_threads);

	_chdir(g_strPath.c_str());
	ofstream fout;

	try {
		fout.open((output_file_name + ".pak").c_str(), ios::out | ios::binary);
	}
	catch (...) {
		cout << "Failed creating output file." << endl;
		return nullptr;
	}

	fout << ".HUFFMAN";
	WriteLong(fout, map.size());

	for (auto iter = map.begin(); iter != map.end(); ++iter)
	{
		fout.put(iter->first);
		WriteDoubleLong(fout, iter->second);
	}

	WriteLong(fout, file_list.size());
	fout.write(output_name.c_str(), output_name.size());
	fout.write(output_context.c_str(), output_context.size());

	fout.close();
	cout << "Write ends." << endl;

	return head;
}