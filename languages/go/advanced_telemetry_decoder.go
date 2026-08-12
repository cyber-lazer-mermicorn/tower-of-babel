// Advanced exhibit: versioned telemetry trust boundary with metrics.
// Owns boundary: magic/version, CRC32, sequence continuity, size caps,
// partial-frame rejection, decode counters. Fail-closed. No placeholders.

package main

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
)

const (
	magic   uint32 = 0x544F4252 // TOBR
	version uint16 = 1
	maxBody        = 1024
)

type Frame struct {
	Seq  uint32
	Kind uint16
	Body []byte
}

type Metrics struct {
	Decoded  int
	Rejected int
	CRCFails int
	SeqGaps  int
	Oversize int
}

type Decoder struct {
	expectSeq uint32
	metrics   Metrics
}

func (d *Decoder) Decode(buf []byte) (Frame, error) {
	if len(buf) < 14 {
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("short frame")
	}
	m := binary.BigEndian.Uint32(buf[0:4])
	if m != magic {
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("bad magic")
	}
	ver := binary.BigEndian.Uint16(buf[4:6])
	if ver != version {
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("bad version")
	}
	seq := binary.BigEndian.Uint32(buf[6:10])
	kind := binary.BigEndian.Uint16(buf[10:12])
	blen := binary.BigEndian.Uint16(buf[12:14])
	if int(blen) > maxBody {
		d.metrics.Oversize++
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("oversize body")
	}
	need := 14 + int(blen) + 4
	if len(buf) < need {
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("truncated")
	}
	body := buf[14 : 14+int(blen)]
	wantCRC := binary.BigEndian.Uint32(buf[14+int(blen) : need])
	gotCRC := crc32.ChecksumIEEE(buf[0 : 14+int(blen)])
	if wantCRC != gotCRC {
		d.metrics.CRCFails++
		d.metrics.Rejected++
		return Frame{}, fmt.Errorf("crc mismatch")
	}
	if seq != d.expectSeq {
		d.metrics.SeqGaps++
	}
	d.expectSeq = seq + 1
	d.metrics.Decoded++
	out := make([]byte, len(body))
	copy(out, body)
	return Frame{Seq: seq, Kind: kind, Body: out}, nil
}

func encode(seq uint32, kind uint16, body []byte) []byte {
	buf := make([]byte, 14+len(body)+4)
	binary.BigEndian.PutUint32(buf[0:4], magic)
	binary.BigEndian.PutUint16(buf[4:6], version)
	binary.BigEndian.PutUint32(buf[6:10], seq)
	binary.BigEndian.PutUint16(buf[10:12], kind)
	binary.BigEndian.PutUint16(buf[12:14], uint16(len(body)))
	copy(buf[14:], body)
	crc := crc32.ChecksumIEEE(buf[0 : 14+len(body)])
	binary.BigEndian.PutUint32(buf[14+len(body):], crc)
	return buf
}

func main() {
	d := &Decoder{}
	f1 := encode(0, 1, []byte("hello"))
	f2 := encode(1, 2, []byte("world"))
	bad := append([]byte{}, f1...)
	bad[len(bad)-1] ^= 0xff

	if _, err := d.Decode(f1); err != nil {
		panic(err)
	}
	if _, err := d.Decode(f2); err != nil {
		panic(err)
	}
	if _, err := d.Decode(bad); err == nil {
		panic("expected crc fail")
	}
	if d.metrics.Decoded != 2 || d.metrics.CRCFails != 1 {
		panic(fmt.Sprintf("metrics %#v", d.metrics))
	}
	fmt.Printf("advanced_telemetry_decoder: ok decoded=%d crc_fails=%d rejected=%d\n",
		d.metrics.Decoded, d.metrics.CRCFails, d.metrics.Rejected)
}
