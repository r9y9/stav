package main

/// Mel-cepstrum extraction for speech signal based on the WORLD.

import (
	"./vc"
	"flag"
	"fmt"
	"github.com/r9y9/gossp/io"
	"github.com/r9y9/gossp/mgcep"
	"github.com/r9y9/nnet"
	"log"
	"time"
)

func main() {
	sfilename := flag.String("src", "src.wav", "Source speaker audio filename")
	ofilename := flag.String("o", "mcep.json", "Output filename(*.json)")
	order := flag.Int("order", 32, "Order of mel-cepstrum")
	flag.Parse()

	src, err := io.ReadWav(*sfilename)
	if err != nil {
		log.Fatal(err)
	}
	srcData := src.GetMonoData()
	sampleRate := int(src.SampleRate)

	m := vc.MCepData{
		FrameShift: int(float64(src.SampleRate) * float64(0.005)),
		SampleRate: int(src.SampleRate),
		FrameLen:   1024,
		NumMceps:   *order,
		Alpha:      mgcep.CalcMCepAlpha(int(src.SampleRate)),
		WindowType: "World",
	}

	length := float64(len(srcData)) / float64(src.SampleRate)
	fmt.Println("Audio length (sec):", length)

	now := time.Now()
	m.Data = vc.GetMCepBasedOnWorld(srcData, sampleRate, m.NumMceps, m.Alpha)
	fmt.Println("Elapsed time in spectral envelope extraction:", time.Now().Sub(now))

	derr := nnet.DumpAsJson(*ofilename, m)
	if derr != nil {
		log.Fatal(derr)
	}
	fmt.Println("Mel-cepstrum written in", *ofilename)
}
