<?php
require __DIR__ . '/vendor/autoload.php';
require __DIR__ . '/database.php';
use Monolog\Logger;
use Monolog\Handler\StreamHandler;
use Monolog\Handler\FirePHPHandler;
if (!function_exists('getallheaders')) 
{ 
    function getallheaders() 
    { 
           $headers = ''; 
       foreach ($_SERVER as $name => $value) 
       { 
           if (substr($name, 0, 5) == 'HTTP_') 
           { 
               $headers[str_replace(' ', '-', ucwords(strtolower(str_replace('_', ' ', substr($name, 5)))))] = $value; 
           } 
       } 
       return $headers; 
    } 
} 
// Create the logger
$logger = new Logger("IFTTT");
// Now add some handlers
$dateStr = date("Ymd_H");
$logger->pushHandler(new StreamHandler(__DIR__."/logs/ifttt_access_$dateStr.log", Logger::DEBUG));
$logger->pushHandler(new FirePHPHandler());
// You can now use your logger
#$logger->info('finish initiating logger');
$requestMethod = $_SERVER["REQUEST_METHOD"];
if ($requestMethod == "POST") {
  $payload = file_get_contents("php://input");
} else {
  $payload = [];
}
$phpFile = arrayGet($_SERVER, "PHP_SELF");
$queryStr = arrayGet($_SERVER, "QUERY_STRING", NULL);
$remoteAddr = arrayGet($_SERVER, "REMOTE_ADDR", NULL);
$timeStamp = arrayGet($_SERVER, "REQUEST_TIME", NULL);
$requestTime = date("Y-m-d H:i:s.u");
$requestHeaders = getallheaders();
$logger->info("new request:$phpFile?$queryStr from $remoteAddr\t", array("payload" => $payload, "requestHeaders"=> $requestHeaders, "requests" => $_SERVER,));

$requestSelfInfo = array(
  "requestFile" => $phpFile,
  "requestQueryStr" => $queryStr,
  "remoteAdd" => $remoteAddr,
  "timeStamp" => $timeStamp,
  "requestTime" => $requestTime,
  #"requestHeaders" => $requestHeaders,
);
function initApi() {
  $requiredChannelKey = "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd0";
#$requestChannelKey = $_
#$headers = apache_request_headers();
  $channelHeaderName = "HTTP_IFTTT_CHANNEL_KEY";
  if (array_key_exists($channelHeaderName, $_SERVER) ) {
	$requestChannelKey = $_SERVER[$channelHeaderName];
  } else {
	$requestChannelKey = "";
  }
#print_r($_SERVER);
  if (strcmp($requestChannelKey, $requiredChannelKey) == 0) {
	return 200;
  } else{
	return 401;
  }
}

function initSelfApi() {
  $requiredChannelKey = "ARQP1psdWjdMG4HENv4zWbWhnUzg4nyQ1nnbLYGPY3jO-YS6L11Y_mW3jUa0dTd";
  $requestHeaders = getallheaders();
#$requestChannelKey = $_
#$headers = apache_request_headers();
  $channelHeaderName = "Self-Channel-Key";
  if (array_key_exists($channelHeaderName, $requestHeaders) ) {
	$requestChannelKey = $requestHeaders[$channelHeaderName];
  } else {
	$requestChannelKey = "";
  }
#print_r($_SERVER);
  if (strcmp($requestChannelKey, $requiredChannelKey) == 0) {
	return 200;
  } else{
	return 401;
  }
}

#log current request to 
#trigger 1, action 2 realtimeapi: 3, others 0
function logRequest2Mysql($requestInfo, $responseInfo, $requestTime, $type = 0) {
  global $mysqlObj;
  $requestStr = json_encode($requestInfo);
  #$responseStr = json_encode($responseInfo);
  $responseStr = "";
  $result = insertToLog($mysqlObj, $requestStr, $responseStr, $requestTime, $type);
  return $result;
}
function initNormalResponse($responseStatus = 200, $isJson = true) {
  http_response_code($responseStatus);
  header("Content-Type: application/json; charset=utf-8");
}

function arrayGet($array, $key, $defaultValue = NULL) {
  if (array_key_exists($key, $array)) {
	return $array[$key];
  } else {
	return $defaultValue;
  }
}
