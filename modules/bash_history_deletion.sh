#!/bin/bash

users=("$@") #read arguments
if [ $# != 0 ]
then #argument supplied
    for i in "${users[@]}"
    do
        user_home=$(awk -v u="$i" -v FS=':' '$1==u {print $6}' /etc/passwd) #get users home from /etc/passwd
        rm $user_home/.bash_history #rm supplied user's bash_history
    done
else #no argument supplied
    rm $HOME/.bash_history #rm running user bash history
fi