# Passive Sonar WebAudio Experiments

This code has experiments on developing a passive sonar with the WebAudio API on mobile devices.

The ultimate goal is to:
 1. Take advantage of the fact modern Android devices have two microphones and two speakers (top and bottom).
 2. Use the WebAudio API to read both audio streams simultaneously.
 3. Measure the time delay between the signals on both mics.

To accomplish that:
 1. First measure the base delay between mics. This can be done by playing a tone on the speakers and see how much difference there is between them and the different mics.
 2. Then use the microphones to listen on a specific frequency range.
 3. Then use [GCC-PHAT](http://www.xavieranguera.com/phdthesis/node92.html) to calculate the time difference of arrival (TDOA) between the two microphones.

This should then at least indicate to the user whether the source of the sound is closer to the right or left microphone.

If successful, an application of this idea could be simple mobile web app to help locate the source of sound (use gyroscope and camera to help the user navigate towards the source of the sound).

**The status of this project is still quite experimental.**

The code seems to be capturing the right data in sync (using [audio worklets](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Using_AudioWorklet)), and seems to be able to calculate the TDOA correctly ([see python visualization here](https://colab.research.google.com/drive/1oor9REZsP6v_C2c1IHQ1AE-sJfD_l2Ax#scrollTo=BE-Dtl3o-1XE)).

Capture happens in a worklet, which copies data to a sharedarraybuffer of both channels simultaneously, as to minimize delay. Processing happens on another JavaScript Worker, which reads the SharedArrayBuffer and calculates the time delay. This calculation is slow (a few seconds behind real time), but can happen in parallel in multiple Workers. The processing is done in JavaScript using Tensorflow.JS, but it could be done in WebAsm, GPU or WebRTC if/when TensorFlow.JS implements the appropriate functions (main problem is complex numbers matrix multiplications).
