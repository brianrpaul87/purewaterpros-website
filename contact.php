<?php
declare(strict_types=1);

$to = 'info@purewaterpros.ca';
$fromSite = 'Pure Water Pros <no-reply@purewaterpros.ca>';

function clean_field(string $key, int $max = 4000): string {
    $value = isset($_POST[$key]) ? trim(strip_tags((string) $_POST[$key])) : '';
    $value = str_replace(["\r\n", "\r"], "\n", $value);
    return substr($value, 0, $max);
}

function single_line(string $value): string {
    return trim(str_replace(["\r", "\n"], ' ', $value));
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: /#launch-request', true, 303);
    exit;
}

// Honeypot: silently accept apparent bot submissions without sending email.
if (clean_field('website', 200) !== '') {
    header('Location: /thank-you.html', true, 303);
    exit;
}

$name = single_line(clean_field('name', 160));
$email = single_line(clean_field('email', 254));
$phone = single_line(clean_field('phone', 80));
$postalCode = single_line(clean_field('postal_code', 24));
$waterSource = single_line(clean_field('water_source', 80));
$subjectSelection = single_line(clean_field('subject', 120));
$message = clean_field('message', 5000);
$diagnostic = clean_field('diagnostic_summary', 5000);
$consent = single_line(clean_field('consent', 40));

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: /?form=missing#launch-request', true, 303);
    exit;
}

if ($consent !== 'accepted') {
    header('Location: /?form=consent#launch-request', true, 303);
    exit;
}

$allowedWaterSources = [
    'Not sure',
    'Private well',
    'Municipal water'
];
if (!in_array($waterSource, $allowedWaterSources, true)) {
    $waterSource = 'Not sure';
}

$allowedSubjects = [
    'Pre-launch water assessment',
    'Existing equipment service',
    'Water softener',
    'Iron or sulfur treatment',
    'UV disinfection',
    'Reverse osmosis drinking water',
    'Chemical injection or oxidation',
    'Low-yield well storage or cistern',
    'General pre-launch question'
];
if (!in_array($subjectSelection, $allowedSubjects, true)) {
    $subjectSelection = 'General pre-launch question';
}

$safeReplyTo = str_replace(["\r", "\n"], '', $email);
$safeName = single_line($name);
$safeSubjectSelection = single_line($subjectSelection);

$subject = "Pre-launch request: {$safeSubjectSelection} — {$safeName}";
$body = "New Pure Water Pros pre-launch request\n\n";
$body .= "Name: {$name}\n";
$body .= "Email: {$email}\n";
$body .= "Phone: " . ($phone !== '' ? $phone : 'Not provided') . "\n";
$body .= "Postal code: " . ($postalCode !== '' ? $postalCode : 'Not provided') . "\n";
$body .= "Water source: {$waterSource}\n";
$body .= "Request type: {$subjectSelection}\n";
$body .= "Pre-launch consent: accepted\n\n";
$body .= "Customer message:\n" . ($message !== '' ? $message : 'No additional message') . "\n\n";

if ($diagnostic !== '') {
    $body .= "Water Problem Checker summary:\n{$diagnostic}\n\n";
}

$body .= "Pre-launch notice acknowledged: service is not currently operating and opening is planned for September 2026 and the requested appointment is not confirmed until direct follow-up.\n";
$body .= "\n— Sent from purewaterpros.ca";

$headers = "From: {$fromSite}\r\n";
$headers .= "Reply-To: {$safeReplyTo}\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: PHP/" . phpversion();

$sent = @mail($to, $subject, $body, $headers);

if ($sent) {
    header('Location: /thank-you.html', true, 303);
} else {
    header('Location: /?form=send#launch-request', true, 303);
}
exit;
?>
