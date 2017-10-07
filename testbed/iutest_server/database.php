<?php
class Event {
  public $deviceId = NULL;
  public $userId = NULL;
  public $eventTime = NULL;
  public $deviceState = NULL;
}
class Log {
  public $type = NULL;
  public $id = NULL;
  public $startTime = NULL;
  public $endTime = NULL;
  public $numLimit = NULL;
}
class Action {
  public $id = NULL;
  public $deviceId = NULL;
  public $deviceState = NULL;
  public $isFinished  = 0;
  public $startTime = NULL;
  public $endTime = NULL;
  public $numLimit = 10;
}
function getDeviceObj ($mysqlObj, $deviceId) {
  $escapedDeviceId = $mysqlObj->escape_string($deviceId);
  $query = "SELECT * from device where id = $escapedDeviceId;";
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  }
  return $result->fetch_assoc();
}
function updateDeviceObj ($mysqlObj, $deviceId, $deviceState) {
  $escapedDeviceId = $mysqlObj->escape_string($deviceId);
  $escapedDeviceState = $mysqlObj->escape_string($deviceState);
  $query = "UPDATE device SET deviceState = $escapedDeviceState WHERE id = $escapedDeviceId;";
  $result = $mysqlObj->query($query);
  return $result;
}

function addDeviceEvent ($mysqlObj, $eventObj) {
  $deviceId = $mysqlObj->escape_string($eventObj->deviceId);
  $deviceState = $mysqlObj->escape_string($eventObj->deviceState);
  $userId = $mysqlObj->escape_string($eventObj->userId);
  $eventTime = $mysqlObj->escape_string($eventObj->eventTime);
  $query = "INSERT INTO event (deviceId, userId, eventTime, deviceState) VALUES($deviceId, $userId, \"$eventTime\", $deviceState);";
  $result = $mysqlObj->query($query);
  return $result;
}

function getDeviceList ($mysqlObj, $deviceType = "light", $userId = 1) {
  $userId = $mysqlObj->escape_string($userId);
  $deviceType = $mysqlObj->escape_string($deviceType);
  $query = "SELECT * FROM device WHERE deviceType = \"$deviceType\" and userId = $userId";
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  } else {
	return $result->fetch_all(MYSQLI_BOTH);
  }
}

function getDeviceEventList($mysqlObj, $deviceId, $deviceState = 1, $eventLimit = 50, $userId = 1) {
  $userId = $mysqlObj->escape_string($userId);
  $deviceId = $mysqlObj->escape_string($deviceId);
  $deviceState = $mysqlObj->escape_string($deviceState);
  $eventLimit = $mysqlObj->escape_string($eventLimit);
  $query = "SELECT * FROM event WHERE deviceId = $deviceId and deviceState = $deviceState and userId = $userId ORDER BY eventTime desc LIMIT $eventLimit";
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  } else {
	return $result->fetch_all(MYSQLI_BOTH);
  }
}

function getAction($mysqlObj, $actionObj) {
  $query = "Select * from action";
  if ( ! is_null($actionObj->id) ) {
	$query .= " where id >= $actionObj->id";
  } else {
	$query .= " where id >= 0";
  }
  if ( ! is_null($actionObj->deviceId) ) {
	$query .= " and deviceId = $actionObj->deviceId";
  }
  if ( !is_null($actionObj->startTime) ) {
	$query .= " and createTime > \"$actionObj->startTime\"";
  }
  if ( !is_null($actionObj->endTime) ) {
	$query .= " and createTime < \"$actionObj->endTime\"";
  }
  if ( ! is_null($actionObj->isFinished)) {
	$query .= " and finished = $actionObj->isFinished";
  } else {
	$query .= " and finished = 0";
  }
  if ( !is_null($actionObj->numLimit) ) {
	$query .= " order by createTime desc limit $actionObj->numLimit";
  } else {
	$query .= " order by createTime desc limit 10";
  }
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  } else {
	return $result->fetch_all(MYSQLI_BOTH);
  }
}
function updateActionState($mysqlObj, $actionId, $actionState) {
  $query = "update action set finished = $actionState, updateTime = NOW() where id = $actionId";
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return False;
  } else {
	return True;
  }
}

function insertToDoDeviceEvent($mysqlObj, $deviceId, $deviceState, $userId = 1) {
  $deviceId = $mysqlObj->escape_string($deviceId);
  $deviceState = $mysqlObj->escape_string($deviceState);
  $userId = $mysqlObj->escape_string($userId);
  $query = "INSERT INTO action (deviceId, deviceState, createTime, finished, userId) VALUES($deviceId, $deviceState, NOW(), 0, $userId);";
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  } else {
	return $mysqlObj->insert_id;
  }
}

function insertToLog($mysqlObj, $requestStr, $responseStr, $logTime, $type) {
  $requestStr = $mysqlObj->escape_string($requestStr);
  $responseStr = $mysqlObj->escape_string($responseStr);
  $logTime = $mysqlObj->escape_string($logTime);
  $query = "INSERT INTO log(time, type, requestDetail, responseDetail) Values(\"$logTime\", $type, \"$requestStr\", \"$responseStr\");";
  $result = $mysqlObj->query($query);
  return $result;
}

function insertLog($mysqlObj, $logType, $logTime, $logMessage) {
  $logMessage = $mysqlObj->escape_string($logMessage);
  $logTime = $mysqlObj->escape_string($logTime);
  $query = "INSERT INTO log(time, type, requestDetail) Values(\"$logTime\", $logType, \"$logMessage\");";
  $result = $mysqlObj->query($query);
  return $result;
}
function getLog($mysqlObj, $logObj) {
  $query = "Select id, time, type, requestDetail, responseDetail from log";
  if ( ! is_null($logObj->id) ) {
	$query .= " where id >= $logObj->id";
  } else {
	$query .= " where id >= 0";
  }
  if ( ! is_null($logObj->type) ) {
	$query .= " and type = $logObj->type";
  }
  if ( !is_null($logObj->startTime) ) {
	$query .= " and time > \"$logObj->startTime\"";
  }
  if ( !is_null($logObj->endTime) ) {
	$query .= " and time < \"$logObj->endTime\"";
  }
  if ( !is_null($logObj->numLimit) ) {
	$query .= " order by time desc limit $logObj->numLimit";
  } else {
	$query .= " order by time desc limit 10";
  }
  $result = $mysqlObj->query($query);
  if ($result == FALSE) {
	return NULL;
  } else {
	return $result->fetch_all(MYSQLI_BOTH);
  }
}

$mysqlObj = new mysqli($host = "localhost", $username = "root", $passwd = "tangmi911", $dbname = "ifttt", $port = 3306);
