<?php
// Receives the "Besichtigung anfragen" request and forwards it by e-mail.
const RECIPIENT = 'kikitoseb@msn.com';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function fail(int $code, string $msg): void {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail(405, 'POST only');

// Same-origin only.
$host = $_SERVER['HTTP_HOST'] ?? '';
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && parse_url($origin, PHP_URL_HOST) !== preg_replace('/:\d+$/', '', $host)) fail(403, 'forbidden');

$raw = file_get_contents('php://input', false, null, 0, 20000);
$data = json_decode($raw ?: '', true);
if (!is_array($data)) fail(400, 'invalid json');

$phone = trim((string)($data['phone'] ?? ''));
if (!preg_match('/^\+?[0-9 ()\/.-]+$/', $phone) || strlen(preg_replace('/\D/', '', $phone)) < 7 || strlen(preg_replace('/\D/', '', $phone)) > 15) {
    fail(422, 'invalid phone');
}

// Simple rate limit: one request per 20 s per IP.
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$stamp = sys_get_temp_dir() . '/fc_' . md5($ip);
if (is_file($stamp) && time() - filemtime($stamp) < 20) fail(429, 'too many requests');
touch($stamp);

function clean($v): string {
    return trim(preg_replace('/[\r\n]+/', ' ', mb_substr((string)$v, 0, 200)));
}
$a = is_array($data['answers'] ?? null) ? $data['answers'] : [];
$r = is_array($data['result'] ?? null) ? $data['result'] : [];

$lines = [
    'Neue Besichtigungsanfrage',
    '',
    'Telefon: ' . clean($phone),
    'E-Mail: ' . clean($a['email'] ?? '—'),
    'PLZ: ' . clean($a['plz'] ?? '—'),
    'Symptom: ' . clean($a['symptom'] ?? '—'),
    'Zeitpunkt: ' . clean($a['timing'] ?? '—'),
    'Gebäudeart: ' . clean($a['buildingType'] ?? '—'),
    'Baujahr: ' . clean($a['buildingYear'] ?? '—'),
    'Problemgröße: ' . clean($a['problemSize'] ?? '—'),
    'Länge: ' . clean($a['problemLength'] ?? '—'),
    '',
    'Diagnose: ' . clean($r['diagnosis'] ?? '—'),
    'Kostenspanne: ' . clean($r['costMin'] ?? '—') . ' – ' . clean($r['costMax'] ?? '—') . ' EUR',
    '',
    'Gesendet: ' . date('Y-m-d H:i:s') . ' (' . $host . ')',
];

$domain = preg_replace('/^www\./', '', preg_replace('/:\d+$/', '', $host));
$headers = [
    'From: FeuchteCheck <no-reply@' . $domain . '>',
    'Content-Type: text/plain; charset=UTF-8',
];
$ok = mail(RECIPIENT, '=?UTF-8?B?' . base64_encode('Besichtigungsanfrage – ' . clean($phone)) . '?=', implode("\n", $lines), implode("\r\n", $headers));
if (!$ok) fail(500, 'mail failed');
echo json_encode(['ok' => true]);
