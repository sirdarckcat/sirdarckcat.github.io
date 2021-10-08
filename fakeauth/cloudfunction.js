/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */
exports.execute = async (req, res) => {
  console.log(req.headers.authorization + JSON.stringify(req.body));
  if (!req.headers.authorization) {
    console.log('sending oauth');
    const rrr = {
      "token_type": "Bearer",
      "access_token": "ACCESSTOKEN",
      "refresh_token": "REFRESHTOKEN",
      "expires_in": 3600
    };
    res.status(200).send(rrr);
    return;
  }
  const response = {requestId: req.body.requestId, payload: {agentUserId: "elgato-user-id"}};
  for (let input of req.body.inputs) {
    switch (input.intent) {
      case "action.devices.SYNC":
        console.log('SYNC');
        response.payload.devices = [];
        response.payload.devices.push({
            id: "elgato-device-id",
            type: 'action.devices.types.LIGHT',
            traits: [
              'action.devices.traits.OnOff',
              'action.devices.traits.ColorSetting',
              'action.devices.traits.Brightness'
            ],
            name: {
              name: "El Gato",
            },
            willReportState: false,
            "otherDeviceIds": [{
              "deviceId": "local-elgato-device-id"
            }],
            "customData": {"foo":"bar"},
            "attributes": {
              "colorTemperatureRange": {
                "temperatureMinK": 2900,
                "temperatureMaxK": 7000
              }
            }
          });
      break;
      case "action.devices.QUERY":
        console.log('QUERY');
        response.payload.devices = {};
      break;
      default:
        console.log('idk', input.intent);
    }
  }
  res.status(200).send(response);
};
