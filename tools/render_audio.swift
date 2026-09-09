// Render build/performance.json to a WAV file.
//
// Uses AVAudioUnitSampler with the sound bank that ships with macOS, so there
// is no soundfont to install. Rendering is offline (faster than real time) and
// deterministic: the same performance.json always produces the same audio.
//
// Usage: swift tools/render_audio.swift build/performance.json build/piece.wav

import AVFoundation
import AudioToolbox
import Foundation

struct Event: Decodable {
    let time: Double
    let type: String
    let channel: UInt8
    let note: UInt8?
    let velocity: UInt8?
    let value: UInt8?
}

struct Performance: Decodable {
    let duration: Double
    let events: [Event]
}

func die(_ message: String) -> Never {
    FileHandle.standardError.write(Data("render_audio: \(message)\n".utf8))
    exit(1)
}

let arguments = CommandLine.arguments
guard arguments.count == 3 else {
    die("usage: swift tools/render_audio.swift <performance.json> <out.wav>")
}

let soundBank = URL(fileURLWithPath:
    "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")
guard FileManager.default.fileExists(atPath: soundBank.path) else {
    die("the macOS sound bank is missing at \(soundBank.path). Audio rendering "
        + "needs it; the MIDI and score outputs do not.")
}

let performance: Performance
do {
    let data = try Data(contentsOf: URL(fileURLWithPath: arguments[1]))
    performance = try JSONDecoder().decode(Performance.self, from: data)
} catch {
    die("could not read \(arguments[1]): \(error.localizedDescription)")
}
guard performance.duration > 0 else { die("the performance has zero duration.") }

let sampleRate = 44100.0
let engine = AVAudioEngine()
let sampler = AVAudioUnitSampler()
let reverb = AVAudioUnitReverb()
engine.attach(sampler)
engine.attach(reverb)

guard let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate,
                                 channels: 2) else {
    die("could not create the output audio format.")
}
engine.connect(sampler, to: reverb, format: format)
engine.connect(reverb, to: engine.mainMixerNode, format: format)
reverb.loadFactoryPreset(.mediumHall)
reverb.wetDryMix = 12
sampler.overallGain = 0

do {
    try sampler.loadSoundBankInstrument(
        at: soundBank, program: 0,
        bankMSB: UInt8(kAUSampler_DefaultMelodicBankMSB), bankLSB: 0)
    try engine.enableManualRenderingMode(.offline, format: format,
                                         maximumFrameCount: 1024)
    try engine.start()
} catch {
    die("could not start the audio engine: \(error.localizedDescription)")
}

// Write a plain 16-bit little-endian PCM WAV: the engine renders in 32-bit
// float, but that format is not what most tools and players expect.
let outputSettings: [String: Any] = [
    AVFormatIDKey: kAudioFormatLinearPCM,
    AVSampleRateKey: sampleRate,
    AVNumberOfChannelsKey: 2,
    AVLinearPCMBitDepthKey: 16,
    AVLinearPCMIsFloatKey: false,
    AVLinearPCMIsBigEndianKey: false,
    AVLinearPCMIsNonInterleaved: false,
]

var file: AVAudioFile?
do {
    file = try AVAudioFile(forWriting: URL(fileURLWithPath: arguments[2]),
                           settings: outputSettings)
} catch {
    die("could not open \(arguments[2]) for writing: \(error.localizedDescription)")
}

guard let buffer = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat,
                                    frameCapacity: 1024) else {
    die("could not allocate the render buffer.")
}

let totalFrames = Int64((performance.duration * sampleRate).rounded())
let events = performance.events.sorted { $0.time < $1.time }
var cursor: Int64 = 0
var index = 0
var stalls = 0
var peak: Float = 0

while cursor < totalFrames {
    // Dispatch every event whose time has arrived.
    while index < events.count,
          Int64((events[index].time * sampleRate).rounded()) <= cursor {
        let event = events[index]
        switch event.type {
        case "on":
            if let note = event.note {
                sampler.startNote(note, withVelocity: event.velocity ?? 64,
                                  onChannel: event.channel)
            }
        case "off":
            if let note = event.note {
                sampler.stopNote(note, onChannel: event.channel)
            }
        case "pedal":
            sampler.sendController(64, withValue: event.value ?? 0,
                                   onChannel: event.channel)
        default:
            die("unknown event type \(event.type.debugDescription) at "
                + "\(event.time)s.")
        }
        index += 1
    }

    // Render only as far as the next event, so timing stays sample-accurate.
    let nextEvent = index < events.count
        ? Int64((events[index].time * sampleRate).rounded()) : totalFrames
    let frames = AVAudioFrameCount(min(1024, min(totalFrames - cursor,
                                                 max(1, nextEvent - cursor))))
    do {
        switch try engine.renderOffline(frames, to: buffer) {
        case .success:
            try file?.write(from: buffer)
            if let channels = buffer.floatChannelData {
                for channel in 0..<Int(buffer.format.channelCount) {
                    for frame in 0..<Int(buffer.frameLength) {
                        peak = max(peak, abs(channels[channel][frame]))
                    }
                }
            }
            cursor += Int64(buffer.frameLength)
            stalls = 0
        case .cannotDoInCurrentContext, .insufficientDataFromInputNode:
            stalls += 1
            if stalls > 100 { die("the offline renderer stalled.") }
        case .error:
            die("the audio renderer reported an error.")
        @unknown default:
            die("the audio renderer returned an unrecognised status.")
        }
    } catch {
        die("rendering failed: \(error.localizedDescription)")
    }
}

engine.stop()
file = nil  // Close the writer so the WAV header lengths are finalised.

let seconds = Double(cursor) / sampleRate
let dbfs = peak > 0 ? 20 * log10(Double(peak)) : -.infinity
print(String(format: "Rendered %.2fs, %d events, peak %.2f dBFS",
             seconds, index, dbfs))
if peak > 0.999 { print("WARNING: the audio is clipping. Reduce the dynamics.") }
if peak < 0.02 { print("WARNING: the audio is nearly silent.") }
