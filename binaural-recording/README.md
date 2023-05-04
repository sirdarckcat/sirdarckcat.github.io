# Binaural Recorder experiment

This tries to merge multiple mics into one output on multiple channels.

https://sirdarckcat.github.io/binaural-recording

Proof of concept works, but requires calibration. For calibration it could use gcc-phat (see /eear) to calculate the shift from the mics
https://github.com/sirdarckcat/sirdarckcat.github.io/commit/effa8dd35fb72ae8c1abad11c4531feeb7bb3da1

Then it may be possible to apply a [delaynode](https://developer.mozilla.org/en-US/docs/Web/API/DelayNode/DelayNode) to reduce or eliminate the delay.

