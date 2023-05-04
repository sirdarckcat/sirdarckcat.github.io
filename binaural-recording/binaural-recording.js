console.log('binaural-recording');

const KNOWN_GOOD_MICS = ['Speakerphone', 'Headset earpiece'];
const KNOWN_BAD_MICS = ['Default', '']; // Bluetooth headset

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
    output.textContent += o.map(o=>{
      const asJson = JSON.stringify(o);
      if (asJson.match(/\w/)) {
        return asJson;
      }
      return o.toString();
    }).join(' ') + '\n';
  };
  try {
    try {
      const permission = await navigator.permissions.query({ name: 'microphone' });
      log(permission);
    } catch(e) {
      log("Permission Error", e);
    }
    const media = await navigator.mediaDevices.getUserMedia({ audio: true });
    log(media);
    const devices = await navigator.mediaDevices.enumerateDevices();
    log(devices);
    const audioDevices = devices.filter(device => device.kind == 'audioinput' && device.deviceId != 'default' && KNOWN_GOOD_MICS.includes(device.label));
    log(audioDevices);
    media.getTracks().forEach(track => track.stop());
    const deviceStreams = await Promise.all(
      audioDevices.map(audioDevice => navigator.mediaDevices.getUserMedia({
        audio: {
          autoGainControl: false,
          channelCount: 1,
          echoCancellation: {exact: false},
          latency: 0,
          noiseSuppression: false,
          sampleRate: 16000, // 48000
          sampleSize: 16,
          deviceId: {
            exact: audioDevice.deviceId
          }
        }
      })));
    log(deviceStreams);
    const audioContext = new AudioContext();
    log(audioContext);
    const micMerger = audioContext.createChannelMerger(deviceStreams.length);
    log(micMerger);
    const outputs = deviceStreams.map((deviceStream, index) => audioContext.createMediaStreamSource(deviceStream).connect(micMerger, 0, index));
    log(outputs);
    const recordedChunks = [];
    const micDestination = audioContext.createMediaStreamDestination();
    micDestination.channelCount = deviceStreams.length;
    log(micDestination);
    micMerger.connect(micDestination);
    console.log("connected micMerger to micDestination");
    const mediaRecorder = new MediaRecorder(micDestination.stream, {mimeType: 'audio/webm'});
    log(mediaRecorder);
    mediaRecorder.addEventListener('dataavailable', function(e) {
      if (e.data.size > 0) recordedChunks.push(e.data);
    });
    mediaRecorder.addEventListener('stop', function() {
      log("creating download");
      downloadLink.href = URL.createObjectURL(new Blob(recordedChunks));
      downloadLink.download = 'recording.wav';
    });
    await new Promise(r=>setTimeout(r, 1e3));
    await audioContext.resume();
    log("audio context started");
    await new Promise(r=>setTimeout(r, 1e3));
    mediaRecorder.start();
    log("media recorder started");
    const speakerMerger = audioContext.createChannelMerger(2);
    const oscillatorLeft = new OscillatorNode(audioContext, {
      type: "sine",
      frequency: 7040,
    });
    const oscillatorRight = new OscillatorNode(audioContext, {
      type: "sine",
      frequency: 3520,
    });
    const oscillatorCenter = new OscillatorNode(audioContext, {
      type: "sine",
      frequency: 2093,
    }); 
    oscillatorLeft.connect(speakerMerger, 0, 0);
    oscillatorRight.connect(speakerMerger, 0, 1);
    oscillatorCenter.connect(audioContext.destination);
    speakerMerger.connect(audioContext.destination);
    const soundStart = audioContext.currentTime + 1;
    oscillatorCenter.start(soundStart);
    oscillatorLeft.start(soundStart + 0.01);
    oscillatorRight.start(soundStart + 0.02);
    oscillatorLeft.stop(soundStart + 0.03);
    oscillatorRight.stop(soundStart + 0.04);
    oscillatorCenter.stop(soundStart + 0.05);
    await new Promise(r=>setTimeout(r, 10e3));
    mediaRecorder.stop();
    log("media recorder stopped");
  } catch(e) {
    log("Error", e);
  }
};
