package main

import (
	"./vc"
	"flag"
	"fmt"
	"github.com/r9y9/go-dsp/wav"
	"github.com/r9y9/gossp/excite"
	"github.com/r9y9/gossp/f0"
	"github.com/r9y9/gossp/io"
	"github.com/r9y9/gossp/vocoder"
	"log"
	"time"
)

func main() {
	ifilename := flag.String("i", "input.wav", "Input wav filename")
	sfilename := flag.String("mcep", "mcep.json", "Mel-cepstrum")
	ofilename := flag.String("o", "output.wav", "Output filename")
	differencial := flag.Bool("diff", false, "Use differencial spectral feature")
	flag.Parse()

	w, werr := io.ReadWav(*ifilename)
	if werr != nil {
		log.Fatal(werr)
	}
	data := w.GetMonoData()

	src, serr := vc.LoadMCep(*sfilename)
	if serr != nil {
		log.Fatal(serr)
	}

	start := time.Now()

	frameShift := src.FrameShift
	sampleRate := src.SampleRate
	alpha := src.Alpha
	order := src.NumMceps
	pd := 5

	var input []float64

	// Perform differencial spectral compensation
	if *differencial {
		length := (len(src.Data) - 1) * frameShift
		input = data[:length]

		// ignore power coefficient!
		for i := range src.Data {
			src.Data[i][0] = 0.0
		}
		src.Data = src.Data[:len(src.Data)-1]
	} else {
		f0Seq := f0.SWIPE(data, sampleRate, frameShift, 60.0, 700.0)
		ex := excite.NewPulseExcite(sampleRate, frameShift)
		input = ex.Generate(f0Seq[:len(src.Data)])
	}

	synth := vocoder.NewMLSASpeechSynthesizer(order, alpha, pd, frameShift)

	// Perform Speech waveform synthesis
	result, err := synth.Synthesis(input, src.Data)
	if err != nil {
		log.Fatal(err)
	}

	////////////////////////////////////////////////////////
	// Output to file
	werr = wav.WriteMono(*ofilename, result, w.SampleRate)
	if werr != nil {
		log.Fatal(werr)
	}

	fmt.Println("Finished", time.Now().Sub(start))
}
