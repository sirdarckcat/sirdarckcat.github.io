console.log('eear');
onload = async function () {
  const output = document.getElementById('output');
  if (!output) {
    alert('No output');
    location.reload();
    return;
  }
  let sw = await navigator.serviceWorker.getRegistration();
  if (!sw) {
    let sw = navigator.serviceWorker.register('sw.js');
    await sw.active;
    try {
      new SharedArrayBuffer(1);
      console.log('SABs ready');
    } catch (e) {
      location.reload();
      return;
    }
  }
  if (!crossOriginIsolated) {
    alert('Failed to enter secure isolated context');
    confirm('Reload?') && location.reload();
  }
  const N = 4096 * 4;
  const sab1 = new SharedArrayBuffer(N * 4 * 2);
  const sab2 = new SharedArrayBuffer(N * 4 * 2);
  const off1 = new SharedArrayBuffer(4);
  const off2 = new SharedArrayBuffer(4);
  const pause = new SharedArrayBuffer(4);
  const permission = await navigator.permissions.query({ name: 'microphone' });
  console.log(permission);
  const media = await navigator.mediaDevices.getUserMedia({ audio: true });
  console.log(media);
  const devices = await navigator.mediaDevices.enumerateDevices();
  console.log(devices);
  const audioDevices = devices.filter(device => device.kind == 'audioinput' && device.deviceId != 'default');
  console.log(audioDevices);
  media.getTracks().forEach(track => track.stop());
  const deviceStreams = await Promise.all(audioDevices.map(audioDevice => navigator.mediaDevices.getUserMedia({ audio: { autoGainControl: false, channelCount: 2, echoCancellation: false, latency: 0, noiseSuppression: false, sampleRate: 48000, sampleSize: 16, volume: 1.0, deviceId: { exact: audioDevice.deviceId } } })));
  console.log(deviceStreams);
  const audioContext = new AudioContext();
  console.log(audioContext);
  await audioContext.audioWorklet.addModule("processor1.js");
  const workletNode = new AudioWorkletNode(audioContext, "my-audio-processor", { numberOfInputs: deviceStreams.length });
  console.log(workletNode);
  workletNode.port.postMessage({ type: 'setSabs', sab1, sab2, off1, off2, pause, N });
  workletNode.port.onmessage = async e => {
    if (e.data.type != 'setSampleRate') return;
    const worker = new Worker('worker.js', { type: "module" });
    console.log(worker);
    const mc = new MessageChannel;
    worker.postMessage({ type: 'setSabs', sab1, sab2, off1, off2, pause, N, sampleRate: e.data.sampleRate }, [mc.port1]);
    await new Promise(res=>mc.port2.onmessage = res);
    while(true) {
      const mc = new MessageChannel;
      worker.postMessage({type: 'getShift'}, [mc.port1]);
      const data = await new Promise(res=>mc.port2.onmessage = e=>res(e.data));
      console.log(data);
      output.appendChild(document.createTextNode(JSON.stringify(data)+"\n"));
    }
  };
  deviceStreams.forEach((deviceStream, index) => audioContext.createMediaStreamSource(deviceStream).connect(workletNode, 0, index));
  await audioContext.resume();
};
