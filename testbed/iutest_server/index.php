<?php
include "init.php";
#logRequest2Mysql($requestInfo, array(), $requestTime, $type = 0);
$logObj = new Log();
$logObj->startTime = "2017-05-10 12:12:40";
$result = getLog($mysqlObj, $logObj);
print(count($result));
if ($result == NULL) {
  echo "no results";
  echo $result;
} else{
  $resultJson = json_encode($result);
  echo $resultJson;
}

