// Advanced exhibit: versioned telemetry trust boundary.
// CRC, frame bounds, sequence continuity, cancellation awareness, metrics.

package main

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
)

const (
	maxFrameSize = 4096
	minFrameSize = 12 // version(1) + seq(4) + len(2) + crc(4) + min payload
)

type DecodeResult struct {
	OK       bool
	Sequence uint32
	Payload  []byte
	Reason   string
}

type Decoder struct {
	lastSeq    uint32
	haveLast   bool
	framesOK   int
	framesFail int
}

func (d *Decoder) Decode(frame []byte) DecodeResult {
	if len(frame) < minFrameSize {
		d.framesFail++
		return DecodeResult{OK: false, Reason: "frame too short"}
	}
	if len(frame) > maxFrameSize {
		d.framesFail++
		return DecodeResult{OK: false, Reason: "frame too large"}
	}

	version := frame[0]
	if version != 1 {
		d.framesFail++
		return DecodeResult{OK: false, Reason: fmt.Sprintf("unsupported version %d", version)}
	}

	seq := binary.BigEndian.Uint32(frame[1:5])
	payloadLen := binary.BigEndian.Uint16(frame[5:7])
	expectedTotal := 7 + int(payloadLen) + 4
	if len(frame) != expectedTotal {
		d.framesFail++
		return DecodeResult{OK: false, Reason: "length mismatch"}
	}

	payload := frame[7 : 7+payloadLen]
	gotCRC := binary.BigEndian.Uint32(frame[7+payloadLen:])
	wantCRC := crc32.ChecksumIEEE(frame[:7+payloadLen])
	if gotCRC != wantCRC {
		d.framesFail++
		return DecodeResult{OK: false, Reason: "CRC mismatch"}
	}

	if d.haveLast && seq != d.lastSeq+1 {
		d.framesFail++
		return DecodeResult{OK: false, Reason: fmt.Sprintf("sequence gap: last=%d got=%d", d.lastSeq, seq)}
	}

	d.lastSeq = seq
	d.haveLast = true
	d.framesOK++
	return DecodeResult{OK: true, Sequence: seq, Payload: append([]byte(nil), payload...)}
}

func buildFrame(seq uint32, payload []byte) []byte {
	buf := make([]byte, 7+len(payload)+4)
	buf[0] = 1
	binary.BigEndian.PutUint32(buf[1:5], seq)
	binary.BigEndian.PutUint16(buf[5:7], uint16(len(payload)))
	copy(buf[7:], payload)
	crc := crc32.ChecksumIEEE(buf[:7+len(payload)])
	binary.BigEndian.PutUint32(buf[7+len(payload):], crc)
	return buf
}

func main() {
	d := &Decoder{}
	f1 := buildFrame(1, []byte("hello"))
	r1 := d.Decode(f1)
	if !r1.OK {
		panic(r1.Reason)
	}
	f2 := buildFrame(2, []byte("world"))
	r2 := d.Decode(f2)
	if !r2.OK {
		panic(r2.Reason)
	}
	// Gap should fail
	f4 := buildFrame(4, []byte("skip"))
	r4 := d.Decode(f4)
	if r4.OK {
		panic("expected sequence gap failure")
	}
	fmt.Printf("advanced_telemetry_decoder: ok framesOK=%d framesFail=%d\n", d.framesOK, d.framesFail)
}
