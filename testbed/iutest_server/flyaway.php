<?php
$entityBody = file_get_contents('php://input');
$dateStr = date("Y-m-d_H-i-s");
file_put_contents("results_$dateStr", $entityBody);
