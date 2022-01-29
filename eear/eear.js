console.log('eear');
onload = async function () {
  const permission = await navigator.permissions.query({name: 'microphone'});
  console.log(permission);
  const media = await navigator.mediaDevices.getUserMedia({audio: true});
  console.log(media);
  const devices = await navigator.mediaDevices.enumerateDevices();
  console.log(devices);
  const audioDevices = devices.filter(device=>device.kind=='audioinput');
  console.log(audioDevices);
  media.getTracks().forEach(track=>track.stop());
  const deviceStreams = await Promise.all(audioDevices.map(audioDevice=>navigator.mediaDevices.getUserMedia({audio: {exact: audioDevice.deviceId}})));
  console.log(deviceStreams);
  const audioContext = new AudioContext();
  await audioContext.resume();
  console.log(audioContext);
  await audioContext.audioWorklet.addModule("processor1.js");
  const workletNode = new AudioWorkletNode(audioContext, "my-audio-processor", {numberOfInputs: deviceStreams.length});
  console.log(workletNode);
  deviceStreams.forEach((deviceStream, index)=>audioContext.createMediaStreamSource(deviceStream).connect(workletNode, 0, index));
  // deviceStreams.forEach((deviceStream, index)=>{
  //   const oscillatorNode = audioContext.createOscillator();
  //   oscillatorNode.type = 'square';
  //   oscillatorNode.frequency.setValueAtTime(3000, audioContext.currentTime + index);
  //   oscillatorNode.connect(workletNode, 0, index);
  //   oscillatorNode.start();
  // });
};
