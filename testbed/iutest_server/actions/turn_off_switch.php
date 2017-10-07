<?php
$basicDeviceType = "switch";
$basicDeviceState = 0;
$basicActionFieldName = "which_switch_to_turn_off";
$fKey = "fieldName";
$oKey = "operation";
include "../init.php";
#logRequest2Mysql($requestInfo, array(), $requestTime, $type = 2);
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
  if (!array_key_exists("actionFields", $postJson) or empty($postJson["actionFields"]) ) {
	$resultData = [
	  "errors" => [
		array("message" => "no action field found",),
	  ],
	];
	initNormalResponse(400);
	echo json_encode($resultData);
	exit;
  }
  $deviceId = $postJson["actionFields"][$basicActionFieldName];
  $result = insertTodoDeviceEvent($mysqlObj, $deviceId, $basicDeviceState);
  if ($result == FALSE) {
	$resultData = [
	  "errors" => [
		array("message" => "internal error",),
	  ],
	];
	initNormalResponse(500);
	#logRequest2Mysql($requestInfo, $resultData, $requestTime, $type = 2);
	echo json_encode($resultData);
	exit;
  }
  $resultData = array(
	"data" => array ( ["id" => $result,],),
  );
  initNormalResponse();
  logRequest2Mysql($requestSelfInfo, $resultData, $requestTime, $type = 2);
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
