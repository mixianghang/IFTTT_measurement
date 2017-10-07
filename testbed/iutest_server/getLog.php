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
$numLimit = 10;
$startTime = arrayGet($postData, "startTime");
$endTime = arrayGet($postData, "endTime");
$type = arrayGet($postData, "type");
$startId = arrayGet($postData, "startId");
#if ( is_null($userId) || is_null($deviceId) || is_null($deviceState) ) {
#  initNormalResponse($responseStatus = 400);
#  #print_r($postData);
#  $resultData = array(
#	"errors" => array(
#	  array("message" => "post data is missing"),
#	),
#  );
#  echo json_encode($resultData);
#  exit;
#}

$logObj = new Log();
$logObj->type = $type;
$logObj->numLimit = $numLimit;
$logObj->id = $startId;
$logObj->startTime = $startTime;
$logObj->endTime = $endTime;
$result = getLog($mysqlObj, $logObj);
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
