#include "base.h"

#pragma warning(disable: 6031)

using namespace std;
using namespace chrono_literals;

using table = unordered_map<char, long long>;
using cstrmap = unordered_map<char, string>;

// TODO: Get huffman-encoded string of each character.
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

// TODO: Get tree size with pre-order traversal.
unsigned int TreeSize(unique_ptr<node_t>& node)
{
	if (node == nullptr)
		return 0;

	unsigned int size = 1;
	size += TreeSize(node->left);
	size += TreeSize(node->right);
	return size;
}

// TODO: Write long to stream as character array.
void WriteLong(ofstream& stream, long l)
{
	union swap {
		long l;
		char c[4];
	} temp;
	temp.l = l;

	stream.write(temp.c, 4);
}

// TODO: Write double long to stream as character array.
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

	mutex mtx; // Mutual exculsive lock

	ifstream fin; // file to read

	int thread_running = 0;
	vector<future<void>> sub_threads; // thread list
	sub_threads.reserve(10); // reserve for maximum size.

	table map; // an unordered_map(hashmap) to save the char and its frequency.
	function read_task = [&map, &mtx](const char* buf, unsigned long long i, int length) { // a lambda function for reading task in thread
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
				// TODO: limit the number of running threads under 10 to prevent system from full threading
				// (That makes a huge lag on low performance computer like my one.)
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

			for (auto& th : sub_threads) // waiting for running threads (read complete)
				while (th.wait_for(0ms) != future_status::ready); // join

			sub_threads.clear(); // Clear it for next file read

			buf.reset(); // initialize dynamically allocated buffer.
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	if (!map.size()) // nothing read :(
		return nullptr;

	vector<unique_ptr<node_t>> counter; // A unique pointer vector container for construct huffman tree (it will be leaf node.)
	counter.reserve(map.size()); // reserve for leaf node size.

	pcll value;
	for (auto iter = map.begin(); iter != map.end(); ++iter)
	{
		value = make_pair(iter->first, iter->second); // assign in to lvalue (rvalue cannot use in make_unique function since it uses &(ref) variable.)
		counter.push_back(make_unique<node_t>(value)); // assign
	}

	cout << "Character count complete. (Total " << counter.size() << ")" << endl;

	while (counter.size() != 1) // Repeat until there is only one node remains (last node = head(root) node)
	{
		auto fmin = counter.end(); // first minimum one
		auto smin = counter.end(); // second minimum one

		for (auto iter = counter.begin(); iter != counter.end(); ++iter)
		{
			if (fmin == counter.end()) // assign first
			{
				fmin = iter;
				continue;
			}

			if (smin == counter.end()) // assign second
			{
				smin = iter;
				continue;
			}

			if ((*fmin)->value.second > (*iter)->value.second) // find first
				fmin = iter;
			else if ((*smin)->value.second > (*iter)->value.second) // find second
				smin = iter;
		}

		if (fmin == counter.end() || smin == counter.end()) // one of them is nullptr: you entered in this loop with (size <= 1) vector or ...(just a weird case)
			return nullptr;

		auto fptr = move(*fmin); // move unique pointer to new one (since the selected ones would be deleted.)
		auto sptr = move(*smin); // same task.

		// TODO: switch node for deleting with last node and pop back.
		// Why we make turn(order) on it?: the swapping can affect actual data on more than one of those iterators(fmin, smin).
		// So we consdier the order to avoid this.
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

		value = make_pair(0, fptr->value.second + sptr->value.second); // Make a new node
		counter.push_back(make_unique<node_t>(fptr, value, sptr));
	}

	auto head = move(counter.front()); // Root node
	cout << "Tree construction complete. (Total " << TreeSize(head) << " nodes)" << endl;

	cstrmap char_map;
	Make_HuffmanMap(char_map, head, ""); // Obtain huffman_string from huffman tree.

	cout << "Huffman tree construction complete. (Total " << char_map.size() << ")" << endl;

	function write_task = [&char_map](const char* buf, vector<bool>& wbuf, unsigned long long i, int length) { // a lambda function for writing task.
		string str = "";
		for (unsigned long long i = 0; i < length; i++)
			str += char_map.at(buf[i]);

		for (auto c : str)
			wbuf.push_back((c - '0') ? true : false);
	};

	i = 0;
	string output_name = ""; // context saves file name, offset and actual size.
	string output_context = ""; // context saves context in file.

	// Sub-buffer vector<bool> vector container for saving huffman-encoded texts.
	// We divide each results in threads in here and merge all element in here.
	vector<vector<bool>> sub_buffer;

	function swritel = [](string& string, long l) { // lambda function for write long(4 bytes) as char(1 byte) * 4 in string
		union swap { // unionnn :) - member in union shares the memory. we can easily switch long to char.
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

			output_name += file; // push name
			output_name.push_back('\0'); // end of string.
			swritel(output_name, output_context.size()); // write(size)

			auto file_size = filesystem::file_size(file);
			auto buf = make_unique<char[]>(file_size);

			fin.read(buf.get(), file_size);

			int sub_buf_size = file_size / length;
			if (file_size % length)
				sub_buf_size++;

			sub_buffer.reserve(sub_buf_size);

			for (unsigned long long i = 0; i < file_size; i += length)
			{
				// I explained it before. :)
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

			// saves real length of file. (since we use long to save data, there could be free(remaining) space in context.
			int total_length = 0;
			for (auto& sub : sub_buffer)
			{
				total_length += sub.size();
				for (int i = 0; i < sub.size(); i += 32) // sizeof(long) = 4, 4 * 8 = 32.
				{
					int iMin = min(i + 32, (int)sub.size()); // cut down the actual size.
					long l = 0;

					// TODO: convert vector<bool> elements as long.
					for (int j = i; j < iMin; j++)
					{
						if (sub[j] == true)
							l |= (1 << (j + i));
					}
					swritel(output_context, l); // write(context)
				}
				vector<bool>().swap(sub); // release memory of vector container.
			}
			swritel(output_name, total_length);
			vector<vector<bool>>().swap(sub_buffer); // release memory of vector container.

			buf.reset();
			fin.close();
		}
		catch (...) {
			cout << "Failed open file: " << file << endl;
			return nullptr;
		}
	}

	vector<unique_ptr<node_t>>().swap(counter); // release memory of vector container.
	vector<future<void>>().swap(sub_threads); // release memory of vector container.

	_chdir(g_strPath.c_str()); // reset path

	// output file stream
	ofstream fout;

	try {
		// ...\data -> data.pak
		fout.open((output_file_name + ".pak").c_str(), ios::out | ios::binary);
	}
	catch (...) {
		cout << "Failed creating output file." << endl;
		return nullptr;
	}

	fout << ".HUFFMAN"; // keycode to check this package is huffman encoded one.
	WriteLong(fout, map.size()); // write size of leaf nodes

	for (auto iter = map.begin(); iter != map.end(); ++iter) // write leaf nodes (1 + 8)[char, long long]{character, number}.
	{
		fout.put(iter->first);
		WriteDoubleLong(fout, iter->second);
	}

	WriteLong(fout, file_list.size()); // write the number of files.
	fout.write(output_name.c_str(), output_name.size()); // write file name, offset, real length.
	fout.write(output_context.c_str(), output_context.size()); // write encoded file context.

	fout.close();
	cout << "Write ends." << endl;

	return head;
}