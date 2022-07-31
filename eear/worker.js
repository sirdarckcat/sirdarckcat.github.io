import "./tf-core.js";
// import "./tf-backend-cpu.js";
// import "./tf-backend-wasm.js";
import "./tf-backend-webgl.js";
import { RingBufferReader } from "./ring-buffer.js";

tf.ready();

class TDOAWorker {
  ringBuffer1 = null;
  ringBuffer2 = null;
  N;
  constructor() {
    onmessage = e => {
      switch (e.data.type) {
        case "setSabs":
          this.ringBuffer1 = new RingBufferReader(
            new Float32Array(e.data.sab1), e.data.off1, e.data.pause);
          this.ringBuffer2 = new RingBufferReader(
            new Float32Array(e.data.sab2), e.data.off2, e.data.pause);
          this.N = e.data.N;
          this.sampleRate = e.data.sampleRate;
          e.ports[0].postMessage({});
          break;
        case "getShift":
          const result = this.process();
          e.ports[0].postMessage(result);
      }
    };
  }

  gccPhat(mic1, mic2, sampleRate) {
    const window = tf.signal.hannWindow(this.N);
    const sig = tf.mul(window, mic1);
    const rsig = tf.mul(window, mic2);
    const n = sig.shape[0] + rsig.shape[0];
    const SIG = tf.spectral.rfft(sig, n);
    const RSIG = tf.spectral.rfft(rsig, n);
    const RSIG_conj = tf.complex(tf.real(RSIG), tf.neg(tf.imag(RSIG)));
    const R = tf.mul(SIG, RSIG_conj);
    // R2=R/abs(R)
    const R2 = tf.complex(tf.mul(tf.real(R), tf.divNoNan(1, tf.abs(R))), tf.mul(tf.imag(R), tf.divNoNan(1, tf.abs(R))));
    let cc = tf.reshape(tf.spectral.irfft(R2), [n]);
    const shift = tf.argMax(tf.abs(cc)).arraySync();
    const shiftCorrected = (cc.shape[0] - shift) % cc.shape[0];
    const tau = shiftCorrected / sampleRate;
    return { shift, shiftCorrected, tau, mic1, mic2, cc: cc.arraySync() };
  }

  process() {
    let mic1Raw, mic2Raw;
    do {
      mic1Raw = this.ringBuffer1.last(this.N);
      mic2Raw = this.ringBuffer2.last(this.N);
    } while (mic1Raw.findIndex(x => !x) != -1 || mic2Raw.findIndex(x => !x) != -1);
    this.ringBuffer1.pause();
    this.ringBuffer2.pause();
    const mic1 = mic1Raw.slice();
    const mic2 = mic2Raw.slice();
    this.ringBuffer1.resume();
    this.ringBuffer2.resume();

    return this.gccPhat(mic1, mic2, this.sampleRate);
  }
};

new TDOAWorker();
