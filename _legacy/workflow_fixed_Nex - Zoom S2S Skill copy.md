{
"name": "Nex - Zoom S2S (ANTI GAGAL)",
"nodes": [
{
"parameters": {
"httpMethod": "POST",
"path": "zoom-meeting",
"responseMode": "responseNode",
"options": {}
},
"id": "d8e4efa3-b54c-4609-a89d-55cdb9a3b9fc",
"name": "Webhook",
"type": "n8n-nodes-base.webhook",
"position": [
512,
528
],
"typeVersion": 2.1,
"webhookId": "d07a470e-2aa3-442a-b167-25a854ced581"
},
{
"parameters": {
"method": "POST",
"url": "https://zoom.us/oauth/token?grant_type=account_credentials&account_id=QVU-nLIvSZyX-MonQxyvRQ",
"authentication": "genericCredentialType",
"genericAuthType": "httpBasicAuth",
"sendBody": true,
"contentType": "form-urlencoded",
"bodyParameters": {
"parameters": [
{}
]
},
"options": {}
},
"id": "1078aa75-689a-4416-9656-510e6a98fbef",
"name": "Get Zoom Token",
"type": "n8n-nodes-base.httpRequest",
"position": [
768,
528
],
"typeVersion": 4.4,
"credentials": {
"httpBasicAuth": {
"id": "RXh9XSuBN0f6Z1fI",
"name": "Zoom Credential"
}
}
},
{
"parameters": {
"method": "POST",
"url": "https://api.zoom.us/v2/users/me/meetings",
"sendHeaders": true,
"headerParameters": {
"parameters": [
{
"name": "Authorization",
"value": "=Bearer {{ $node[\"Get Zoom Token\"].json[\"access_token\"] }}"
}
]
},
"sendBody": true,
"specifyBody": "json",
"jsonBody": "={\n \"topic\": \"{{ $node[\"Webhook\"].json[\"body\"][\"params\"][\"topic\"] }}\",\n \"type\": 2,\n \"start*time\": \"{{ $node[\"Webhook\"].json[\"body\"][\"params\"][\"start_time\"] }}\",\n \"duration\": 60,\n \"timezone\": \"Asia/Jakarta\"\n}",
"options": {}
},
"id": "34d11a91-5a5c-4cd0-9123-946b5746efaa",
"name": "Create Zoom Meeting",
"type": "n8n-nodes-base.httpRequest",
"position": [
1024,
528
],
"typeVersion": 4.4
},
{
"parameters": {
"assignments": {
"assignments": [
{
"id": "f1",
"name": "final_link",
"value": "={{ $node[\"Create Zoom Meeting\"].json[\"join_url\"] }}",
"type": "string"
},
{
"id": "f2",
"name": "final_topic",
"value": "={{ $node[\"Create Zoom Meeting\"].json[\"topic\"] }}",
"type": "string"
},
{
"id": "f3",
"name": "final_time",
"value": "={{ $node[\"Create Zoom Meeting\"].json[\"start_time\"] }}",
"type": "string"
}
]
},
"options": {}
},
"id": "e76a4fc0-1108-477d-bffc-600c776056a5",
"name": "Gudang Data",
"type": "n8n-nodes-base.set",
"position": [
1264,
528
],
"typeVersion": 3.4
},
{
"parameters": {
"chatId": "7478935640",
"text": "=📅 \_Meeting Berhasil Dibuat!*\n\n📝 _Topic:_ {{ $node[\"Create Zoom Meeting\"].json[\"topic\"] || \"Tidak ada judul\" }}\n\n⏰ _Waktu:_ {{\n  $node[\"Create Zoom Meeting\"].json[\"start_time\"]\n    ? new Date($node[\"Create Zoom Meeting\"].json[\"start_time\"]).toLocaleString(\"id-ID\", {\n        dateStyle: \"full\",\n        timeStyle: \"short\"\n      })\n    : \"Tidak tersedia\"\n}}\n\n🧑‍💻 _Host:_ {{ $node[\"Create Zoom Meeting\"].json[\"host\"] || \"Tidak diketahui\" }}\n\n🆔 _Meeting ID:_ {{ $node[\"Create Zoom Meeting\"].json[\"id\"] || \"-\" }}\n\n🔗 _Link Meeting:_\n{{ $node[\"Create Zoom Meeting\"].json[\"join_url\"] || \"Link tidak tersedia\" }}\n\n📌 _Catatan:_\nHarap join 5 menit sebelum meeting dimulai.",
"additionalFields": {
"parse_mode": "Markdown"
}
},
"id": "cea5254a-3749-47e6-8f7c-54f4f5607186",
"name": "Telegram Notify",
"type": "n8n-nodes-base.telegram",
"position": [
1520,
528
],
"typeVersion": 1.2,
"webhookId": "6183b96f-acd0-43c7-a66a-cc99e4f32cfd",
"credentials": {
"telegramApi": {
"id": "SwoFHLUQ8zl11LBQ",
"name": "Telegram account"
}
}
},
{
"parameters": {
"respondWith": "json",
"responseBody": "={{ {\n  status: \"success\",\n  id: $node[\"Create Zoom Meeting\"].json[\"id\"],\n  topic: $node[\"Create Zoom Meeting\"].json[\"topic\"],\n  start_time: $node[\"Create Zoom Meeting\"].json[\"start_time\"],\n  join_url: $node[\"Create Zoom Meeting\"].json[\"join_url\"],\n  host: $node[\"Create Zoom Meeting\"].json[\"host_email\"]\n} }}",
"options": {}
},
"id": "59842dfb-0e56-4715-a12b-a1c18a83f730",
"name": "Respond to Agent",
"type": "n8n-nodes-base.respondToWebhook",
"position": [
1776,
528
],
"typeVersion": 1.5
}
],
"pinData": {},
"connections": {
"Webhook": {
"main": [
[
{
"node": "Get Zoom Token",
"type": "main",
"index": 0
}
]
]
},
"Get Zoom Token": {
"main": [
[
{
"node": "Create Zoom Meeting",
"type": "main",
"index": 0
}
]
]
},
"Create Zoom Meeting": {
"main": [
[
{
"node": "Gudang Data",
"type": "main",
"index": 0
}
]
]
},
"Gudang Data": {
"main": [
[
{
"node": "Telegram Notify",
"type": "main",
"index": 0
}
]
]
},
"Telegram Notify": {
"main": [
[
{
"node": "Respond to Agent",
"type": "main",
"index": 0
}
]
]
}
},
"active": true,
"settings": {
"executionOrder": "v1",
"binaryMode": "separate"
},
"versionId": "4c79f342-d090-46b2-ae12-15dccb3ba77d",
"meta": {
"templateCredsSetupCompleted": true,
"instanceId": "b35f60998cfe73f0a37ed70adb8b4e092857ec9d25041ac9661c354a0c5add72"
},
"id": "ghdy62KgP20nGIWz",
"tags": []
}
