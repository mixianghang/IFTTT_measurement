<?php
require_once "init.php";
#logRequest2Mysql($requestInfo, array(), $requestTime, $type = 4);
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
$startTime = arrayGet($postData, "startTime");
$endTime = arrayGet($postData, "endTime");
$isFinished = arrayGet($postData, "isFinished");
$startId = arrayGet($postData, "startId");
$deviceId = arrayGet($postData, "deviceId");
$deviceState = arrayGet($postData, "deviceState");
$numLimit = arrayGet($postData, "numLimit");
$actionObj = new Action();
$actionObj->deviceId = $deviceId;
$actionObj->deviceState = $deviceState;
$actionObj->numLimit = $numLimit;
$actionObj->id = $startId;
$actionObj->startTime = $startTime;
$actionObj->endTime = $endTime;
$actionObj->isFinished = $isFinished;
$result = getAction($mysqlObj, $actionObj);
if (!is_null($result)) {
  initNormalResponse($responseStatus = 200);
  $resultData = array(
	"data" => $result,
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
