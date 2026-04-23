{
"name": "Nex - Zoom S2S Skill (FIXED)",
"nodes": [
{
"parameters": {
"httpMethod": "POST",
"path": "skill",
"options": {}
},
"id": "webhook",
"name": "Webhook",
"type": "n8n-nodes-base.webhook",
"position": [200, 300]
},
{
"parameters": {
"functionCode": "if (!$json.skill || !$json.params) {\n throw new Error(\"Invalid payload\");\n}\nreturn items;"
},
"id": "validate",
"name": "Validate",
"type": "n8n-nodes-base.function",
"position": [400, 300]
},
{
"parameters": {
"propertyName": "={{$json[\"skill\"]}}",
"rules": [
{
"value": "create_zoom_meeting"
}
]
},
"id": "switch",
"name": "Switch Skill",
"type": "n8n-nodes-base.switch",
"position": [600, 300]
},
{
"parameters": {
"method": "POST",
"url": "https://zoom.us/oauth/token?grant_type=account_credentials&account_id=YOUR_ACCOUNT_ID",
"authentication": "basicAuth",
"responseFormat": "json"
},
"id": "get_token",
"name": "Get Zoom Token",
"type": "n8n-nodes-base.httpRequest",
"position": [800, 200],
"credentials": {
"httpBasicAuth": {
"id": "YOUR_BASIC_AUTH_ID",
"name": "Zoom S2S Auth"
}
}
},
{
"parameters": {
"method": "POST",
"url": "https://api.zoom.us/v2/users/me/meetings",
"jsonParameters": true,
"bodyParametersJson": "={\n \"topic\": $json[\"params\"][\"topic\"],\n  \"type\": 2,\n  \"start_time\": $json[\"params\"][\"datetime\"],\n  \"duration\": $json[\"params\"][\"duration\"],\n  \"timezone\": \"Asia/Jakarta\"\n}",
        "headerParametersJson": "={\n  \"Authorization\": \"Bearer \" + $node[\"Get Zoom Token\"].json[\"access_token\"]\n}"
      },
      "id": "create_meeting",
      "name": "Create Zoom Meeting",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1000, 300]
    },
    {
      "parameters": {
        "keepOnlySet": true,
        "values": {
          "string": [
            {
              "name": "topic",
              "value": "={{$json[\"topic\"]}}"
},
{
"name": "join_url",
"value": "={{$json[\"join_url\"]}}"
},
{
"name": "start_time",
"value": "={{$json[\"start_time\"]}}"
}
]
}
},
"id": "format",
"name": "Format Result",
"type": "n8n-nodes-base.set",
"position": [1200, 300]
},
{
"parameters": {
"chatId": "YOUR_CHAT_ID",
"text": "📅 Meeting Berhasil Dibuat!\n\n📝 {{$json[\"topic\"]}}\n⏰ {{$json[\"start_time\"]}}\n\n🔗 {{$json[\"join_url\"]}}"
},
"id": "telegram",
"name": "Telegram Notify",
"type": "n8n-nodes-base.telegram",
"position": [1400, 300],
"credentials": {
"telegramApi": {
"id": "YOUR_TELEGRAM_ID",
"name": "Telegram Bot"
}
}
},
{
"parameters": {
"responseData": "={\n \"status\": \"success\",\n \"message\": \"Meeting created\",\n \"join_url\": $json[\"join_url\"]\n}"
},
"id": "respond",
"name": "Respond",
"type": "n8n-nodes-base.respondToWebhook",
"position": [1600, 300]
}
],
"connections": {
"Webhook": {
"main": [[{ "node": "Validate", "type": "main" }]]
},
"Validate": {
"main": [[{ "node": "Switch Skill", "type": "main" }]]
},
"Switch Skill": {
"main": [[{ "node": "Get Zoom Token", "type": "main" }]]
},
"Get Zoom Token": {
"main": [[{ "node": "Create Zoom Meeting", "type": "main" }]]
},
"Create Zoom Meeting": {
"main": [[{ "node": "Format Result", "type": "main" }]]
},
"Format Result": {
"main": [[{ "node": "Telegram Notify", "type": "main" }]]
},
"Telegram Notify": {
"main": [[{ "node": "Respond", "type": "main" }]]
}
}
}
