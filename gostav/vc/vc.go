// Package vc provides utility functions that can be used for voice conversion
// system.
package vc

import (
	"encoding/json"
	"github.com/r9y9/go-world"
	"github.com/r9y9/gossp"
	"github.com/r9y9/gossp/mgcep"
	"math"
	"os"
)

// Feature represents a feature vector (vector of vectors) for a speech signal.
type Feature struct {
	Data [][]float64
}

// MCepData represents Mel-cepstrum feature vector for a speech signal.
// Mel-cepstrum analytics parameters should be stored in this structure.
type MCepData struct {
	Feature
	SampleRate int
	FrameShift int
	FrameLen   int
	NumMceps   int
	Alpha      float64
	WindowType string
}

// ParallelMCepData represents parallel data for voice conversion.
type ParallelMCepData struct {
	Src, Target *MCepData
}

var defaultDioOption = world.DioOption{
	F0Floor:          80.0,
	F0Ceil:           800.0,
	FramePeriod:      5,
	ChannelsInOctave: 4.0,
	Speed:            2,
}

// LoadMCep loads mel-cepstrum from filename and returns the results.
func LoadMCep(filename string) (*MCepData, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	d := &MCepData{}
	err = decoder.Decode(d)

	if err != nil {
		return nil, err
	}

	return d, nil
}

// GetMCepBasedOnWorld computes Mel-cepstrum sequence using the WORLD
// and returns the results.
func GetMCepBasedOnWorld(x []float64, sampleRate, numCeps int,
	alpha float64) [][]float64 {
	w := world.New(sampleRate, defaultDioOption.FramePeriod)

	// 1. Fundamental frequency
	timeAxis, f0 := w.Dio(x, defaultDioOption)

	// 2. Refine F0 estimation result
	f0 = w.StoneMask(x, timeAxis, f0)

	// 3. Spectral envelope
	// spectrogram := w.CheapTrick(x, timeAxis, f0)
	spectrogram := w.Star(x, timeAxis, f0)

	// 4. Mel-cepstrum
	melCepstrogram := make([][]float64, len(spectrogram))
	for i, envelope := range spectrogram {
		amp := gossp.Symmetrize(envelope)
		for i, val := range amp {
			amp[i] = math.Log(val)
		}

		melCepstrogram[i] = mgcep.LogAmp2MCep(amp, numCeps, alpha)
	}

	return melCepstrogram
}

// VC performs voice conversion with a specified mel-cepstrum sequence.
func VC(x []float64, sampleRate, frameShift int, alpha float64,
	mceps [][]float64) []float64 {
	period := int(float64(frameShift) / float64(sampleRate) * 1000.0)
	w := world.New(sampleRate, float64(period))
	defaultDioOption.FramePeriod = float64(period)

	// 1. Fundamental frequency
	timeAxis, f0 := w.Dio(x, defaultDioOption)

	// 2. Refine F0 estimation result
	f0 = w.StoneMask(x, timeAxis, f0)

	// 3. Spectral envelope
	spectrogram := w.Star(x, timeAxis, f0)

	// 4. Excitation spectrum
	residual := w.Platinum(x, timeAxis, f0, spectrogram)

	// VC
	numFreqBins := len(spectrogram[0])
	symmetrizedLen := (numFreqBins-1)*2 + 1
	for i := range spectrogram {
		amp := mgcep.MCep2LogAmp(mceps[i], symmetrizedLen, -alpha)

		// Exp
		for i, val := range amp[:numFreqBins] {
			amp[i] = math.Exp(val)
		}

		spectrogram[i] = amp[:numFreqBins]
	}

	// 5. Synthesis
	return w.Synthesis(f0, spectrogram, residual, len(x))
}
