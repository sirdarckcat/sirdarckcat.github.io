# El Gato Key Light Air - Google Assistant integration

This allows you to control the El Gato Key Light Air through Google Home. It supports brightness and temperature.

You should be able to replicate this by:
  1. Create a Cloud function at https://console.cloud.google.com/functions
  2. Put [cloudfunction.js](cloudfunction.js) on the cloud function.
  3. Deploy the cloud function.
  4. Create a Smart Home action at https://console.actions.google.com/
  5. In fullfilment URL put your cloud function.
  6. In the testing URL for Chrome put https://sirdarckcat.github.io/fakeauth/index.html
  7. In the testing URL for Node put https://sirdarckcat.github.io/fakeauth/bundle.js
  8. In device configuration add 3 scan configs:

    * Scan Config:
      * mDNS service name: `_elg._tcp.local`
      * Name: `elgato.*`
    * Scan Config:
      * mDNS service name: `_elg._tcp`
      * Name: `elgato.*`
    * Scan Config:
      * mDNS service name: `_elg._tcp.local.`
      * Name: `elgato.*`

  9. In the account linking, type `placeholder` in client name and client secret.
  10. Go to tinyurl.com and create a shortlink for https://oauth-redirect.googleusercontent.com/r/YOUR_PROJECT_CODE_HERE?code=1
  11. Type the tinyurl on the Authorization URL
  12. Type your cloud function on the Token URL


**It has only been tested with one light.**
