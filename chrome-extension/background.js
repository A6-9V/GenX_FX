// This is the background script for the GenX FX Trading Chrome Extension.
// It will handle persistent tasks, such as API communication and notifications.

console.log("Background script loaded.");

chrome.runtime.onInstalled.addListener(() => {
  console.log("GenX FX Trading extension installed.");
});
