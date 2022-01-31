import "./tf-core.js";
import "./tf-backend-cpu.js";
// import "./tf-backend-wasm.js";
// import "./tf-backend-webgl.js";
import {RingBufferReader} from "./ring-buffer.js";

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
            new Float32Array(e.data.sab1), e.data.off1);
          this.ringBuffer2 = new RingBufferReader(
            new Float32Array(e.data.sab2), e.data.off2);
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

  gccPhat(mic1, mic2, fs, max_tau=0, interp=16) {
    const window = tf.signal.hannWindow(this.N);
    const sig = tf.mul(window, mic1);
    const rsig = tf.mul(window, mic2);
    const n = sig.shape[0] + rsig.shape[0];
    const SIG = tf.spectral.rfft(sig, n);
    const RSIG = tf.spectral.rfft(rsig, n);
    const RSIG_conj = tf.complex(tf.real(RSIG), tf.neg(tf.imag(RSIG)));
    const R = tf.mul(SIG, RSIG_conj);
    // R2=R/abs(R)
    const R2 = tf.complex(tf.mul(tf.real(R), tf.div(1, tf.abs(R))), tf.mul(tf.imag(R), tf.div(1, tf.abs(R))));
    let cc = tf.reshape(tf.spectral.irfft(R2), [n]);
    let max_shift = interp * n / 2;
    if (max_tau) {
      max_shift = Math.min(interp * fs * max_tau, max_shift)
    }
    cc = tf.concat([
      tf.slice(cc, cc.shape[0] - max_shift, max_shift),
      tf.slice(cc, 0, max_shift + 1)
    ]);
    const shift = tf.argMax(tf.abs(cc));
    const shiftCorrected = shift.arraySync() - max_shift;
    const tau = shiftCorrected / interp * fs;
    return {shift: shiftCorrected, tau};
  }

  process() {
    const sound_speed = 343.2;
    const distance = 0.14;
    const mic1 = tf.tensor1d(this.ringBuffer1.last(this.N));
    const mic2 = tf.tensor1d(this.ringBuffer2.last(this.N));
    const max_tau = distance / sound_speed;

    const tau = this.gccPhat(mic1, mic2, this.sampleRate, max_tau);
    return {tau, theta: Math.asin(tau.tau/max_tau)*180/Math.PI};
  }
};

new TDOAWorker();
