<?php
include "./init.php";
if (!array_key_exists("ignore", $_GET)) {
  $initResult = initApi();
  if ($initResult >= 300) {
	http_response_code($initResult);
	exit();
  }
}
$resultData = array(
  "data" => array(
    "samples" => array(
	  "triggers" => array(
		"light_turned_on" => array(
		  "which_light_is_turned_on" => 2,
		),
		"switch_turned_on" => array(
		  "which_switch_is_turned_on" => 1,
		),
		"switch_turned_off" => array(
		  "which_switch_is_turned_off" => 1,
		),
		"light_turned_off" => array(
		  "which_light_is_turned_off" => 2,
		),
	  ),
	  "actions" => array(
		"turn_on_light" => array(
		  "which_light_to_turn_on" => 2,
		),
		"turn_off_light" => array(
		  "which_light_to_turn_off" => 2,
		),
		"turn_on_switch" => array(
		  "which_switch_to_turn_on" => 1,
		),
		"turn_off_switch" => array(
		  "which_switch_to_turn_off" => 1,
		),
	  ),
	),
  ),
);
initNormalResponse();
echo json_encode($resultData);
exit;
