"use strict";Object.defineProperty(exports, "__esModule", { value: true });exports.default = void 0;var _discovery = require("./discovery.js");
var _configCompat = require("./config-compat.js");
var _pluginEntry = require("openclaw/plugin-sdk/plugin-entry");
//#region extensions/amazon-bedrock/setup-api.ts
var setup_api_default = exports.default = (0, _pluginEntry.definePluginEntry)({
  id: "amazon-bedrock",
  name: "Amazon Bedrock Setup",
  description: "Lightweight Amazon Bedrock setup hooks",
  register(api) {
    api.registerProvider({
      id: "amazon-bedrock",
      label: "Amazon Bedrock",
      auth: [],
      resolveConfigApiKey: ({ env }) => (0, _discovery.resolveBedrockConfigApiKey)(env)
    });
    api.registerConfigMigration((config) => (0, _configCompat.migrateAmazonBedrockLegacyConfig)(config));
  }
});
//#endregion /* v9-8a176b331248b4b5 */
