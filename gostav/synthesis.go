package main

import (
	"./vc"
	"flag"
	"fmt"
	"github.com/r9y9/go-dsp/wav"
	"github.com/r9y9/gossp/io"
	"log"
	"time"
)

func main() {
	ifilename := flag.String("i", "input.wav", "Input wav filename")
	sfilename := flag.String("mcep", "mcep.json", "Mel-cepstrum")
	ofilename := flag.String("o", "output.wav", "Output filename")
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

	result := vc.VC(data, sampleRate, frameShift, alpha, src.Data)

	////////////////////////////////////////////////////////
	// Output to file
	werr = wav.WriteMono(*ofilename, result, w.SampleRate)
	if werr != nil {
		log.Fatal(werr)
	}

	fmt.Println("Finished", time.Now().Sub(start))
}
