<?php
require_once "init.php";
logRequest2Mysql($requestSelfInfo, array(), $requestTime, $type = 20);
$initResult = initSelfApi();
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
$postData = json_decode(file_get_contents("php://input"), $assoc = True);
if ($postData == NULL) {
  initNormalResponse($responseStatus = 400);
  $resultData = array(
	"errors" => array(
	  array("message" => "post data is null"),
	),
  );
  echo json_encode($resultData);
  exit;
}
$userId = arrayGet($postData, "userId");
$deviceId = arrayGet($postData, "deviceId");
$deviceState = arrayGet($postData, "deviceState");
$eventTime = arrayGet($postData, "eventTime");
$deviceName = arrayGet($postData, "deviceName");
if ( is_null($userId) || is_null($deviceId) || is_null($deviceState) ) {
  initNormalResponse($responseStatus = 400);
  #print_r($postData);
  $resultData = array(
	"errors" => array(
	  array("message" => "post data is missing"),
	),
  );
  echo json_encode($resultData);
  exit;
}

#$deviceObj = getDeviceOBj($mysqlObj, strval($deviceId));
#print_r($deviceObj);
#updateDeviceObj($mysqlObj, $deviceId, $deviceState);
#$deviceObj = getDeviceOBj($mysqlObj, strval($deviceId));
#print_r($deviceObj);
$event = New Event();
$event->userId = $userId;
$event->deviceId = $deviceId;
$event->deviceState = $deviceState;
$event->eventTime = $eventTime;
#print_r($event);
$result = addDeviceEvent($mysqlObj, $event);
if ($result == true) {
  initNormalResponse($responseStatus = 200);
  $resultData = array(
	"data" => array(
	  array("message" => "success"),
	),
  );
  echo json_encode($resultData);
  exit;
} else {
  initNormalResponse($responseStatus = 500);
  $resultData = array(
	"data" => array(
	  array("message" => "internal error"),
	),
  );
  echo json_encode($resultData);
  exit;
}
