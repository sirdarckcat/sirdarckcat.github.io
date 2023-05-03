console.log('eear');
onload = async function () {
  try {
    const output = document.getElementById('output');
    const downloadLink = document.getElementById('downloadLink');
    if (!output) {
      alert('No output');
      location.reload();
      return;
    }
    const log = (...o) => {
      console.log(...o);
      output.textContent += o.join(' ') + '\n';
    };
    const permission = await navigator.permissions.query({ name: 'microphone' });
    log(permission);
    const media = await navigator.mediaDevices.getUserMedia({ audio: true });
    log(media);
    const devices = await navigator.mediaDevices.enumerateDevices();
    log(devices);
    const audioDevices = devices.filter(device => device.kind == 'audioinput' && device.deviceId != 'default');
    log(audioDevices);
    media.getTracks().forEach(track => track.stop());
    const deviceStreams = await Promise.all(
      audioDevices.map(audioDevice => navigator.mediaDevices.getUserMedia({
        audio: {
          autoGainControl: false,
          channelCount: 1,
          echoCancellation: false,
          latency: 0,
          noiseSuppression: false,
          sampleRate: 48000,
          sampleSize: 16,
          deviceId: {
            exact: audioDevice.deviceId
          }
        }
      })));
    log(deviceStreams);
    const audioContext = new AudioContext();
    log(audioContext);
    const outputs = deviceStreams.map((deviceStream, index) => audioContext.createMediaStreamSource(deviceStream).connect(workletNode, index));
    log("outputs mapped");
    await audioContext.resume();
    log("audio context started");
    const recordedChunks = [];
    const mediaRecorder = new MediaRecorder(audioCtx.destination, {mimeType: 'audio/webm'});
    log(mediaRecorder);
    mediaRecorder.addEventListener('dataavailable', function(e) {
      if (e.data.size > 0) recordedChunks.push(e.data);
    });
    mediaRecorder.addEventListener('stop', function() {
      log("creating download");
      downloadLink.href = URL.createObjectURL(new Blob(recordedChunks));
      downloadLink.download = 'recording.wav';
    });
    mediaRecorder.start();
    log("starting media recorder");
    await new Promise(r=>setTimeout(r, 10e3));
    log("waited 10s");
    mediaRecorder.stop();
    log("stopped media recorder");
  } catch(e) {
    log("Error", e);
  }
};
