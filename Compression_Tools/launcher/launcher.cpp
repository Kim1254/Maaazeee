// encoder.cpp : 애플리케이션에 대한 진입점을 정의합니다.
//

#include "framework.h"
#include "launcher.h"

#include "shellapi.h"

#include "decode.h"

std::string g_strPath;

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    char current[300];
    _getcwd(current, 300);
    g_strPath = current;

    auto file_list = Parse("data.pak"); // unpack data.

    _chdir(g_strPath.c_str());

    if (!file_list.size()) // data.pak not found or invalid package
    {
        MessageBox(nullptr, L"Cannot find data files! check you have data.pak in game directory.", L"ERROR", MB_OK);
        return 1;
    }

    // Shell execution of the compiled python program. we won't show the execution terminal, but receives the process is terminated,
    SHELLEXECUTEINFO ShExecInfo;
    ShExecInfo.cbSize = sizeof(SHELLEXECUTEINFO);
    ShExecInfo.fMask = SEE_MASK_NOCLOSEPROCESS; // get status
    ShExecInfo.hwnd = NULL;
    ShExecInfo.lpVerb = NULL;
    ShExecInfo.lpFile = _T("main\\main.exe");
    ShExecInfo.lpParameters = NULL;
    ShExecInfo.lpDirectory = NULL;
    ShExecInfo.nShow = SW_HIDE; // we won't show this.
    ShExecInfo.hInstApp = NULL;

    ShellExecuteEx(&ShExecInfo);

    if (WaitForSingleObject(ShExecInfo.hProcess, 500) == WAIT_FAILED) // main\\main.exe not found.
    {
        MessageBox(nullptr, L"Failed starting game process.", L"ERROR", MB_OK);
        return 1;
    }
    else
    {
        while (WaitForSingleObject(ShExecInfo.hProcess, 500) != WAIT_OBJECT_0) {}; // wait til shell terminates.

        auto rm = g_strPath + "\\data";
        RemoveFolder(rm); // remove data we unpacked.
    }
    
    return 0;
}
