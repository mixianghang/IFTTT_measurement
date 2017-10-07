<?php
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
  http_response_code(200);
} else{
  http_response_code(401);
}
