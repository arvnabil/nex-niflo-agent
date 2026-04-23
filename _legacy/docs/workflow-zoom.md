{
"name": "Nex - Zoom S2S Skill",
"nodes": [
{
"parameters": {
"httpMethod": "POST",
"path": "zoom-meeting",
"options": {}
},
"id": "d9fd1baf-8183-4d65-b47b-991564febec2",
"name": "Webhook",
"type": "n8n-nodes-base.webhook",
"position": [
-608,
112
],
"typeVersion": 2.1,
"webhookId": "7e48777c-483b-4658-a36b-5044cf853b1c"
},
{
"parameters": {
"functionCode": "if (!$json.skill || !$json.params) {\n throw new Error(\"Invalid payload\");\n}\nreturn items;"
},
"id": "8abd9bb6-5257-4be8-b0e3-54cc888f81e6",
"name": "Validate",
"type": "n8n-nodes-base.function",
"position": [
-400,
112
],
"typeVersion": 1
},
{
"parameters": {
"options": {}
},
"id": "56939366-3f14-4f6c-91f3-6607f659c224",
"name": "Switch Skill",
"type": "n8n-nodes-base.switch",
"position": [
-208,
112
],
"typeVersion": 3.4
},
{
"parameters": {
"method": "POST",
"url": "https://zoom.us/oauth/token?grant_type=account_credentials&account_id=QVU-nLIvSZyX-MonQxyvRQ",
"authentication": "genericCredentialType",
"genericAuthType": "httpBasicAuth",
"options": {}
},
"id": "79f11519-78f4-4293-a33a-ce4507239d11",
"name": "Get Zoom Token",
"type": "n8n-nodes-base.httpRequest",
"position": [
0,
0
],
"typeVersion": 4.4,
"credentials": {
"httpBasicAuth": {
"id": "RXh9XSuBN0f6Z1fI",
"name": "Unnamed credential"
}
}
},
{
"parameters": {
"method": "POST",
"url": "https://api.zoom.us/v2/users/me/meetings",
"options": {}
},
"id": "39c4cba7-3272-4c6c-9baf-d7b8daa3cfe9",
"name": "Create Zoom Meeting",
"type": "n8n-nodes-base.httpRequest",
"position": [
208,
112
],
"typeVersion": 4.4
},
{
"parameters": {
"options": {}
},
"id": "2c889aa7-9954-4c66-aec3-8519e22b53f0",
"name": "Format Result",
"type": "n8n-nodes-base.set",
"position": [
400,
112
],
"typeVersion": 3.4
},
{
"parameters": {
"chatId": "7478935640",
"text": "📅 Meeting Berhasil Dibuat!\n\n📝 {{$json[\"topic\"]}}\n⏰ {{$json[\"start_time\"]}}\n\n🔗 {{$json[\"join_url\"]}}",
"additionalFields": {}
},
"id": "3b52b286-b5e2-4dc8-9c4f-6c80597fc636",
"name": "Telegram Notify",
"type": "n8n-nodes-base.telegram",
"position": [
608,
112
],
"typeVersion": 1.2,
"webhookId": "232be8e7-36a4-47de-9ea7-d539a01a332f",
"credentials": {
"telegramApi": {
"id": "SwoFHLUQ8zl11LBQ",
"name": "Telegram account"
}
}
},
{
"parameters": {
"options": {}
},
"id": "190c723a-5a5e-40d4-b4f2-dab83a0e7258",
"name": "Respond",
"type": "n8n-nodes-base.respondToWebhook",
"position": [
800,
112
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
"node": "Validate",
"type": "main",
"index": 0
}
]
]
},
"Validate": {
"main": [
[
{
"node": "Switch Skill",
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
"node": "Format Result",
"type": "main",
"index": 0
}
]
]
},
"Format Result": {
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
"node": "Respond",
"type": "main",
"index": 0
}
]
]
}
},
"active": false,
"settings": {
"executionOrder": "v1",
"binaryMode": "separate"
},
"versionId": "3f862933-c13b-44b7-95cf-3cee19b6b47e",
"meta": {
"templateCredsSetupCompleted": true,
"instanceId": "b35f60998cfe73f0a37ed70adb8b4e092857ec9d25041ac9661c354a0c5add72"
},
"id": "ghdy62KgP20nGIWz",
"tags": []
}
