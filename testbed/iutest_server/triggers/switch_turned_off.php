<?php
$basicDeviceType = "switch";
$basicDeviceState = 0;
$basicTriggerFieldName = "which_switch_is_turned_off";
$fKey = "fieldName";
$oKey = "operation";
include "../init.php";
#logRequest2Mysql($requestInfo, array(), $requestTime, $type = 1);
if (!array_key_exists("ignore", $_GET)) {
  $initResult = initApi();
  if ($initResult >= 300) {
	$resultData = array(
	  "errors" => array(
		array("message" => "invalid channel key"),
	  ),
	);
	initNormalResponse($initResult);
	echo json_encode($resultData);
	exit;
  }
}
#$uuid = uniqid("sh_trigger_");
#$timestamp = time();
#$isoDateStr = date(DateTime::ATOM, $timestamp);
$requestInfo = print_r($_SERVER, true);
#$logger->info("request information is $requestInfo");
if (!array_key_exists($fKey, $_GET) or !array_key_exists($oKey, $_GET)) {
  $postdata = file_get_contents("php://input");
  $postJson = json_decode($postdata, true);
  //print_r($postJson);
  if (!empty($postJson) && array_key_exists("limit", $postJson)) {
	$limit = intval($postJson["limit"]);
  } else {
	$limit = 50;
  }
  if (!array_key_exists("triggerFields", $postJson) or empty($postJson["triggerFields"]) ) {
	$resultData = [
	  "errors" => [
		array("message" => "no trigger field found",),
	  ],
	];
	initNormalResponse(400);
	echo json_encode($resultData);
	exit;
  }
  $deviceId = $postJson["triggerFields"][$basicTriggerFieldName];
  if ($limit > 0) {
	$eventList = getDeviceEventList($mysqlObj,  $deviceId, $basicDeviceState, $limit);
	if ($eventList == NULL) {
	  $resultData = [
		"errors" => [
		  array("message" => "internal error",),
		],
	  ];
	  initNormalResponse(500);
	  echo json_encode($resultData);
	  exit;
	}
  } else {
	$eventList = [];
  }
  $triggerItemList = [];
  #print_r($eventList);
  foreach ( $eventList as $event ) {
	#print_r($event);
	$eventTime = $event["eventTime"];
	$eventId = $event["id"];
	$dateTime = DateTime::createFromFormat("Y-m-d H:i:s", $eventTime);
	$timeStamp = $dateTime->getTimeStamp();
	$isoDateStr = date(DateTime::ATOM, $timeStamp);
	$triggerItemList[] = array(
	  "created_at" => $isoDateStr,
	  #"created_at" => "2017-02-07T13:26:49-05:00",
	  #"the_light_turned_on" => "light 1",
	  "meta" => [
		"id" => $eventId,
		"timestamp" => $timeStamp,
	  ],
	);
  }
  $resultData = array(
	"data" => $triggerItemList,
  );
  initNormalResponse();
  logRequest2Mysql($requestSelfInfo, $resultData, $requestTime, $type = 1);
  echo json_encode($resultData);
  exit();
}
$fieldName = $_GET[$fKey];
$operation = $_GET[$oKey];

switch($operation) {
  case "options" : {
	$deviceList = getDeviceList($mysqlObj, $basicDeviceType);
	if ($deviceList == NULL) {
	  $resultData = [
		"errors" => [
		  array("message" => "internal error",),
		],
	  ];
	  initNormalResponse(500);
	  echo json_encode($resultData);
	  exit;
	}
	$resultDeviceList = [];
	foreach($deviceList as $device) {
	  $deviceName = $device["name"];
	  $deviceId = $device["id"];
	  $resultDeviceList[] = [ "label" => $deviceName, "value" => $deviceId ];
	}
	//retrieve options for a field
	$resultData = array(
	  "data" => $resultDeviceList,
	);
	break;
  }
  case "validate" : {
	//validate user input
	break;
  }
}
initNormalResponse();
echo json_encode($resultData);
exit;
