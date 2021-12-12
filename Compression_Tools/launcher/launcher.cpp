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

    auto file_list = Parse("data.pak");

    _chdir(g_strPath.c_str());

    SHELLEXECUTEINFO ShExecInfo;
    ShExecInfo.cbSize = sizeof(SHELLEXECUTEINFO);
    ShExecInfo.fMask = SEE_MASK_NOCLOSEPROCESS;
    ShExecInfo.hwnd = NULL;
    ShExecInfo.lpVerb = NULL;
    ShExecInfo.lpFile = _T("main\\main.exe");
    ShExecInfo.lpParameters = NULL;
    ShExecInfo.lpDirectory = NULL;
    ShExecInfo.nShow = SW_HIDE;
    ShExecInfo.hInstApp = NULL;

    ShellExecuteEx(&ShExecInfo);

    if (WaitForSingleObject(ShExecInfo.hProcess, 500) != WAIT_FAILED)
    {
        while (WaitForSingleObject(ShExecInfo.hProcess, 500) != WAIT_OBJECT_0) {};

        auto rm = g_strPath + "\\data";
        RemoveFolder(rm);
    }
    
    return 0;
}
