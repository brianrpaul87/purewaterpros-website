<?php
$to = 'info@purewaterpros.ca';
$fromSite = 'Pure Water Pros <no-reply@purewaterpros.ca>';

function clean_field($key, $max = 4000) {
    $value = isset($_POST[$key]) ? trim(strip_tags((string) $_POST[$key])) : '';
    $value = str_replace(["\r\n", "\r"], "\n", $value);
    return substr($value, 0, $max);
}

if (clean_field('website', 200) !== '') {
    header('Location: /thank-you.html');
    exit;
}

$name = clean_field('name', 160);
$email = clean_field('email', 254);
$phone = clean_field('phone', 80);
$postalCode = clean_field('postal_code', 24);
$waterSource = clean_field('water_source', 80);
$subjectSelection = clean_field('subject', 120);
$message = clean_field('message', 5000);
$diagnostic = clean_field('diagnostic_summary', 5000);

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: /?form=missing#launch-request');
    exit;
}

$allowedSubjects = [
    'Opening-week water assessment',
    'Existing equipment service',
    'Water softener',
    'Iron or sulfur treatment',
    'UV disinfection',
    'Reverse osmosis drinking water',
    'General pre-launch question'
];
if (!in_array($subjectSelection, $allowedSubjects, true)) {
    $subjectSelection = 'General pre-launch question';
}

$safeReplyTo = str_replace(["\r", "\n"], '', $email);
$subject = "Pre-launch request: {$subjectSelection} — {$name}";
$body = "New Pure Water Pros pre-launch request\n\n";
$body .= "Name: {$name}\n";
$body .= "Email: {$email}\n";
$body .= "Phone: " . ($phone !== '' ? $phone : 'Not provided') . "\n";
$body .= "Postal code: " . ($postalCode !== '' ? $postalCode : 'Not provided') . "\n";
$body .= "Water source: " . ($waterSource !== '' ? $waterSource : 'Not sure') . "\n";
$body .= "Request type: {$subjectSelection}\n\n";
$body .= "Customer message:\n" . ($message !== '' ? $message : 'No additional message') . "\n\n";
if ($diagnostic !== '') {
    $body .= $diagnostic . "\n\n";
}
$body .= "Pre-launch notice acknowledged: service is not currently operating and scheduling is expected to open in August 2026.\n";
$body .= "\n— Sent from purewaterpros.ca";

$headers = "From: {$fromSite}\r\n";
$headers .= "Reply-To: {$safeReplyTo}\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: PHP/" . phpversion();

$sent = @mail($to, $subject, $body, $headers);
if ($sent) {
    header('Location: /thank-you.html');
} else {
    header('Location: /?form=send#launch-request');
}
exit;
?>
