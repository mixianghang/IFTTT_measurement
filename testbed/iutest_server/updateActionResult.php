<?php
require_once "init.php";
logRequest2Mysql($requestSelfInfo, array(), $requestTime, $type = 60);
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
if ( ! is_array($postData)  or count($postData) == 0) {
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

$result = True;
$finishedNum = 0;
foreach ($postData as $actionObj) {
  $actionId = arrayGet($actionObj, "actionId");
  $actionState = arrayGet($actionObj, "actionState");
  if (is_null($actionId) or is_null($actionState)) {
	initNormalResponse($responseStatus = 400);
	#print_r($postData);
	$resultData = array(
	  "errors" => array(
		array("message" => "post data is malformed"),
	  ),
	);
	echo json_encode($resultData);
	exit;
  }
  $result = updateActionState($mysqlObj, $actionId, $actionState);
  if ($result == False) {
	break;
  }
  $finishedNum += 1;
}
if ($result == true) {
  initNormalResponse($responseStatus = 200);
  $resultData = array(
	"data" => array(
	  array("message" => "success $finishedNum updates"),
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
