class MyAudioProcessor extends AudioWorkletProcessor {
  counter = 0;
  differences = null;
  constructor() {
    super();
    this.differences = [];
  }

  process(inputList, outputList, parameters) {
    this.counter++;
    for(let i=0;i<128;i++) {
      for(let j=0;j<inputList.length;j++){
        const baseline = inputList[j][0][i];
        for(let k=j+1;k<inputList.length;k++){
          if (inputList[k][0][i]!=baseline) {
            this.differences.push({
              counter: this.counter,
              sample: i,
              input1: j,
              input2: k
            });
          }
        }
      }
    }
    if(Math.random()<0.001) {
      console.log(this.differences);
      throw new Error('fuck');
    }
    return true;
  }
};

registerProcessor("my-audio-processor", MyAudioProcessor);
