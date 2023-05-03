console.log('eear');
onload = async function () {
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
  try {
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
          autoGainControl: { exact: false },
          channelCount: { exact: 1 },
          echoCancellation: { exact: false },
          latency: { exact: 0 },
          noiseSuppression: { exact: false },
          sampleRate: { exact: 48000 },
          sampleSize: { exact: 16 },
          deviceId: { exact: audioDevice.deviceId }
        }
      })));
    log(deviceStreams);
    const audioContext = new AudioContext();
    log(audioContext);
    const merger = audioContext.createChannelMerger(deviceStreams.length);
    log(merger);
    const outputs = deviceStreams.map((deviceStream, index) => audioContext.createMediaStreamSource(deviceStream).connect(merger, 0, index));
    log(outputs);
    const recordedChunks = [];
    const destination = audioContext.createMediaStreamDestination();
    destination.channelCount = deviceStreams.length;
    log(destination);
    merger.connect(destination);
    console.log("connected merger to destination");
    const mediaRecorder = new MediaRecorder(destination.stream, {mimeType: 'audio/webm'});
    log(mediaRecorder);
    mediaRecorder.addEventListener('dataavailable', function(e) {
      if (e.data.size > 0) recordedChunks.push(e.data);
    });
    mediaRecorder.addEventListener('stop', function() {
      log("creating download");
      downloadLink.href = URL.createObjectURL(new Blob(recordedChunks));
      downloadLink.download = 'recording.wav';
    });
    await audioContext.resume();
    log("audio context started");
    mediaRecorder.start();
    log("media recorder started");
    await new Promise(r=>setTimeout(r, 10e3));
    log("waited 10s");
    mediaRecorder.stop();
    log("media recorder stopped");
  } catch(e) {
    log("Error", e);
  }
};
