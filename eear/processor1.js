import {RingBufferWriter} from "./ring-buffer.js";

class MyAudioProcessor extends AudioWorkletProcessor {
  ringBuffer1 = null;
  ringBuffer2 = null;
  readData = 0;
  started = false;
  N = 0;
  constructor() {
    super();
    this.port.onmessage = e => {
      if (e.data.type != 'setSabs') return;
      this.ringBuffer1 = new RingBufferWriter(
        new Float32Array(e.data.sab1), e.data.off1);
      this.ringBuffer2 = new RingBufferWriter(
        new Float32Array(e.data.sab2), e.data.off2);
      this.N = e.data.N;
    };
    this.port.postMessage({type:'setSampleRate', sampleRate});
  }

  process(inputList, outputList, parameters) {
    if (inputList.length != 2) {
      throw new Error('Need exactly two mics, sorry.');
    }

    if(!this.started && (!inputList[0][0][0] || !inputList[1][0][0])) {
      // mics not sending data yet
      return true;
    }
    if (!this.ringBuffer1 || !this.ringBuffer2) {
      // buffers not ready yet
      return true;
    }
    this.started = true;

    if (inputList[0][0].length != inputList[1][0].length) {
      throw new Error('Sample size is different accross inputs');
    }
    this.ringBuffer1.add(inputList[0][0]);
    this.ringBuffer2.add(inputList[1][0]);
    return true;
  }
};

registerProcessor("my-audio-processor", MyAudioProcessor);
