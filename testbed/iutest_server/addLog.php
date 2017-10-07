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
$logTime = arrayGet($postData, "logTime");
$logType = arrayGet($postData, "logType");
$logMessage = arrayGet($postData, "logMessage");
if ( is_null($logTime) || is_null($logType) || is_null($logMessage) ) {
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

$result = insertLog($mysqlObj, $logType, $logTime, $logMessage);
if (!is_null($result)) {
  initNormalResponse($responseStatus = 200);
  $resultData = array(
	"data" => array (
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
