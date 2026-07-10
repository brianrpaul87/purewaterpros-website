<?php
$to='info@purewaterpros.ca';$from_site='Pure Water Pros <no-reply@purewaterpros.ca>';
function sanitize($k){return isset($_POST[$k])?trim(strip_tags($_POST[$k])):'';}
$name=sanitize('name');$email=sanitize('email');$phone=sanitize('phone');$subjectSel=sanitize('subject');$message=sanitize('message');
if($name===''||$email===''||$phone===''){header('Location:/contact.html?error=missing');exit;}
$subject="New quote request: $subjectSel — $name";
$body="New lead from Pure Water Pros website:\n\nName: $name\nEmail: $email\nPhone: $phone\nInterest: $subjectSel\n\nMessage:\n$message\n\n— Sent from website contact form";
$headers="From: $from_site\r\nReply-To: $email\r\nX-Mailer: PHP/".phpversion();
$sent=@mail($to,$subject,$body,$headers);if($sent){header('Location:/thank-you.html');}else{header('Location:/contact.html?error=send');}exit;
?>