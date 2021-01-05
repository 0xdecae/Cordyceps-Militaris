# Cordyceps Militaris

![alt text](https://github.com/0xdecae/Cordyceps-Militaris/blob/main/Cordyceps-Militaris.png?raw=true)

Command and Control server plus agents. The project is something I've been wanting to write for a very long time. I've had the idea in my mind to try and rewrite the wheel to not only educate myself on languages such as Python3, C/C++, C#, .NET, but the respective Linux and Windows operating systems, and the wonderful WinAPI that comes with. I took inspiration from many blogs and basic tutorials before me, so credit to all those who want to see the InfoSec community grow, and red team ops succeed. Salud.

As for the goal of this hot steamy pile of collegiate angst, we're here. I wanted to create something like Metasploit but that functions the way I want it to and is a mix between recon, automation, exploitation, persistence, and a complete nuisance. So with that, we have a standard C2, but we're going to implement a way to easily write and implement pieces of software or 'modules' to load into it to be fired at the target agent to execute. Of course this is a two-way street, meaning that there will be editing and fixing in both the manager and agent everytime something has to be added, but this is all the fun. Working hard or hardly working, eh? The other major feature of this framework is the implementation of various transport protocols and methods. The prototype works with simple TCP transfer, but our immediate future looks to implement versions that are capable of HTTP and DNS transfer and exfil. After that, ideas spring to mind of using ICMP, SMTP, IRC (oof), FTP[?] or other various protocols.



TODO:
 - Agent
    - Functions
      - Retrieve pid of agent [FIN]
      - Beaconing [WIP]
      - Re-evaluate and clean up shell interaction [WIP]
      - Upload and Download files
    - Formats
      - Create Linux agent
      - Create C# and .NET agent
      - Create DLL agent
    - Module Framework
      - Build
        - Cmds:
	  - load <module>
          - set options?
          - fire
      - [L/W] Module: Move/Copy agent to be executed at startup (research ways to do so)
      - [W] Module: Use the WinAPI to return information and create a profile for a target (See https://github.com/fdiskyou/hunter)
      - [L/W] Module: Evasion implementation and tactics
      - [L/W] Module: Upload and hide Supervisor script which will surveil the agent to recreate and re-execute upon deletion (after a random time period)
      - [L] Module: Transfer and implement Diamorphine
      - [L] Module: Basic BASHRC, PROFILE, or CRON Persistence
    - Size
      - Monitor, keep it small - Remove C++ elements, reduce to strictly C
    - Certification/Authentication
      - Encrypt traffic going to and from
    
- Server
    - Split into seperate python files and classes [FIN]
    - Functions
      - Multi-Listener capabilities
      - Help/usage screen cmd
      - Logging
        - CMD History
        - Connection Init/Loss
        - JSON? DB? txt?
      - ClearScreen cmd [FIN]
      - Profiles : establishment and storage
      - Upload/Download
      - Authentication
      - Certification and Encrypted Traffic
      - Turn the listeners into a class [FIN]
      
    - Improve error handling
       - Fix Ctrl-C [WIP]
       - Ensure that nothing can go wrong in Batch-mode or Interaction-mode : if it does, resolve... [FIN]
    - Transport Mechanisms
      - TCP [WIP]
      - HTTP
      - DNS
      - ICMP
      - FTP
      - SMTP?
      - SNMP?
      - Whatever else Andrew can come up with and implement
