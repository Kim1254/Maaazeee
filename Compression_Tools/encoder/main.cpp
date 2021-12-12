#include "base.h"
#include "encode.h"
#include "decode.h"

using namespace std;

string g_strPath;

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

	if (!std::filesystem::exists(target))
	{
		cout << "File doesn't exist: " << target << endl;
		exit(1);
	}

	vector<string> file_list;
	size_t cut;

	std::function get_last_index = [](string& str, char token) -> int {
		int index = 0;

		const char* p = str.c_str();
		const char* q = strchr(p, token);

		while (q)
		{
			index = q - str.c_str();
			p = q;
			q = strchr(p + 1, token);
		}

		return index;
	};

	if (std::filesystem::is_directory(target))
	{
		SearchFiles(target.c_str(), file_list);
		cut = target.length() + 1; // \\.
	}
	else
	{
		file_list.push_back(target);
		cut = get_last_index(target, '\\') + 1;
	}

	int end = 0;
	string orig_wd = argv[0];
	g_strPath = orig_wd.substr(0, get_last_index(orig_wd, '\\'));

	for (auto iter = file_list.begin(); iter != file_list.end(); ++iter)
		*iter = iter->substr(cut, iter->length());

	if (std::filesystem::is_directory(argv[1]))
		_chdir(argv[1]);

	if (Huffman(file_list) == nullptr)
		cout << "Error: Failed creating output files." << endl;

	system("pause>nul");

	Parse("data.pak");

	system("pause>nul");

	return 1;
}