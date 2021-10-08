"use strict";
/// <reference types="@google/local-home-sdk" />
const app = new smarthome.App("1.0.0");
app.onIdentify((request) => {
    console.debug("IDENTIFY request:", request);
    const device = request.inputs[0].payload.device;
    return new Promise((resolve, reject) => {
        const response = {
            intent: smarthome.Intents.IDENTIFY,
            requestId: request.requestId,
            payload: {
                device: {
                    id: device.id || "",
                    verificationId: "local-elgato-device-id"
                },
            },
        };
        console.debug("IDENTIFY response", response);
        resolve(response);
    });
})
    .onQuery((request) => {
    console.debug("QUERY request", request);
    const devices = {};
    const response = {
        requestId: request.requestId,
        payload: { devices: devices }
    };
    return Promise.all(request.inputs[0].payload.devices.map((device) => {
        const command = new smarthome.DataFlow.HttpRequestData();
        command.requestId = request.requestId;
        command.method = smarthome.Constants.HttpOperation.GET;
        command.deviceId = device.id;
        command.port = 9123;
        command.path = '/elgato/lights';
        return app.getDeviceManager().send(command)
            .then((result) => {
            console.debug("QUERY response", result);
            const httpResult = result;
            const responseBody = httpResult.httpResponse.body;
            const deviceState = JSON.parse(responseBody);
            const lightState = deviceState.lights[0];
            devices[device.id] = {
                "on": !!lightState['on'],
                "color": {
                    "temperatureK": Math.floor(1e6 / lightState['temperature']),
                },
                "brightness": lightState['brightness'],
            };
        });
    })).then(() => {
        return response;
    });
})
    .onExecute((request) => {
    console.debug("EXECUTE request", request);
    const response = new smarthome.Execute.Response.Builder()
        .setRequestId(request.requestId);
    const command = request.inputs[0].payload.commands[0];
    const lightState = {};
    const newState = { "lights": [lightState] };
    for (const exec of command.execution) {
        switch (exec.command) {
            case "action.devices.commands.OnOff":
                lightState['on'] = exec.params.on * 1;
                break;
            case "action.devices.commands.ColorAbsolute":
                lightState['temperature'] = Math.floor(1e6 / exec.params.color.temperature);
                break;
            case "action.devices.commands.BrightnessAbsolute":
                lightState["brightness"] = exec.params.brightness;
                break;
        }
    }
    return Promise.all(command.devices.map((device) => {
        const command = new smarthome.DataFlow.HttpRequestData();
        command.requestId = request.requestId;
        command.deviceId = device.id;
        command.method = smarthome.Constants.HttpOperation.PUT;
        command.port = 9123;
        command.path = '/elgato/lights';
        command.data = JSON.stringify(newState);
        command.dataType = 'application/json';
        return app.getDeviceManager().send(command).then(() => {
            response.setSuccessState(device.id, "FOOBAR");
        }).catch((e) => {
            response.setErrorState(device.id, e);
        });
    })).then(() => {
        console.debug("EXECUTE response", response);
        return response.build();
    });
})
    .listen()
    .then(() => {
    console.log("Ready");
});
