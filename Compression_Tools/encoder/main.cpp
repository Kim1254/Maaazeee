#include "base.h"
#include "encode.h"

using namespace std;

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

	cout << argv[0] << endl;
	string target = argv[1];

	vector<string> file_list;
	SearchFiles(target.c_str(), file_list);

	auto cut = target.length() + 1; // \\

	for (auto iter = file_list.begin(); iter != file_list.end(); ++iter)
		*iter = iter->substr(cut, iter->length());

	_chdir(argv[1]);

	if (Huffman(file_list) == nullptr)
		cout << "Error: Failed creating output files." << endl;

	system("pause>nul");

	return 1;
}