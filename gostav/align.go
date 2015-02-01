package main

import (
	"./vc"
	"flag"
	"fmt"
	"github.com/r9y9/gossp/dtw"
	"github.com/r9y9/gossp/mgcep"
	"github.com/r9y9/nnet"
	"log"
	"math"
	"time"
)

var (
	cutSilence   = true
	cutThreshold = 14.0
)

func main() {
	sfilename := flag.String("src", "src.json", "Source speaker features")
	tfilename := flag.String("target", "target.json", "Target speaker features")
	ofilename := flag.String("o", "parallel.json", "Output filename(*.json)")
	differencial := flag.Bool("diff", false, "Use differencial spectral feature")
	flag.Parse()

	src, serr := vc.LoadMCep(*sfilename)
	if serr != nil {
		log.Fatal(serr)
	}

	tgt, terr := vc.LoadMCep(*tfilename)
	if terr != nil {
		log.Fatal(terr)
	}

	// Align two mcep series
	// ------------------------------------------------------------
	now := time.Now()
	d := &dtw.DTW{ForwardStep: 0, BackwardStep: 2}
	d.SetTemplate(src.Data)
	path := d.DTW(tgt.Data)
	fmt.Println("Elapsed time:", time.Now().Sub(now))

	newTgtMcep := make([][]float64, len(src.Data))
	for i := range newTgtMcep {
		newTgtMcep[i] = make([]float64, len(src.Data[i]))
	}

	for i := range path {
		newTgtMcep[path[i]] = tgt.Data[i]
	}

	// Linear interpolation
	for i, mc := range newTgtMcep {
		if mc[0] == 0.0 && i > 0 && i < len(newTgtMcep)-1 {
			for j := range mc {
				mc[j] = (newTgtMcep[i-1][j] + newTgtMcep[i+1][j]) / 2.0
			}
		}
	}

	src.Data, tgt.Data = src.Data, newTgtMcep

	// ------------------------------------------------------------

	// Cut silence frames
	var srcNew, tgtNew [][]float64
	for i := range src.Data {
		energy := math.Log(mgcep.MCep2Energy(src.Data[i], src.Alpha, src.FrameLen))
		if energy > cutThreshold {
			srcNew = append(srcNew, src.Data[i])
			tgtNew = append(tgtNew, tgt.Data[i])
		}
	}

	if cutSilence {
		src.Data, tgt.Data = srcNew, tgtNew
	}

	if *differencial {
		for t := range tgt.Data {
			for d := range tgt.Data[t] {
				tgt.Data[t][d] = tgt.Data[t][d] - src.Data[t][d]
			}
		}
	}

	m := vc.ParallelMCepData{Src: src, Target: tgt}

	err := nnet.DumpAsJson(*ofilename, m)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Parallel data written in", *ofilename)
}
