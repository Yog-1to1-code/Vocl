package com.vocl.app;

import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.AudioAttributes;
import android.media.MediaRecorder;
import android.util.Log;

public final class AudioStreamEngine {

    private static final String TAG = "AudioStreamEngine";

    private static final int CAPTURE_RATE   = 16000;
    private static final int PLAYBACK_RATE  = 24000;
    private static final int CHANNEL_IN     = AudioFormat.CHANNEL_IN_MONO;
    private static final int CHANNEL_OUT    = AudioFormat.CHANNEL_OUT_MONO;
    private static final int ENCODING       = AudioFormat.ENCODING_PCM_16BIT;
    private static final int CHUNK_DURATION_MS = 100;

    // 16kHz * 2 bytes * 100ms = 3200 bytes per chunk
    public static final int CAPTURE_CHUNK_BYTES = CAPTURE_RATE * 2 * CHUNK_DURATION_MS / 1000;

    private AudioRecord audioRecord;
    private AudioTrack  audioTrack;

    public void initCapture() {
        int minBuffer = AudioRecord.getMinBufferSize(CAPTURE_RATE, CHANNEL_IN, ENCODING);
        int bufferSize = Math.max(minBuffer, CAPTURE_CHUNK_BYTES * 4);
        audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.VOICE_COMMUNICATION,
                CAPTURE_RATE, CHANNEL_IN, ENCODING, bufferSize);
    }

    public void initPlayback() {
        int minBuffer = AudioTrack.getMinBufferSize(PLAYBACK_RATE, CHANNEL_OUT, ENCODING);
        AudioAttributes attrs = new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build();
        AudioFormat format = new AudioFormat.Builder()
                .setSampleRate(PLAYBACK_RATE)
                .setChannelMask(CHANNEL_OUT)
                .setEncoding(ENCODING)
                .build();
        audioTrack = new AudioTrack(attrs, format, Math.max(minBuffer, 8192),
                AudioTrack.MODE_STREAM, AudioTrack.WRITE_NON_BLOCKING);
    }

    public void startCapture() {
        if (audioRecord != null) audioRecord.startRecording();
    }

    public void startPlayback() {
        if (audioTrack != null) audioTrack.play();
    }

    public byte[] readCaptureChunk() {
        if (audioRecord == null) return null;
        byte[] buffer = new byte[CAPTURE_CHUNK_BYTES];
        int read = audioRecord.read(buffer, 0, buffer.length);
        if (read > 0) return buffer;
        return null;
    }

    public void writePlaybackData(byte[] pcmData) {
        if (audioTrack != null) {
            audioTrack.write(pcmData, 0, pcmData.length);
        }
    }

    public void flushPlayback() {
        if (audioTrack == null) return;
        audioTrack.pause();
        audioTrack.flush();
        audioTrack.play();
    }

    public void release() {
        if (audioRecord != null) {
            try { audioRecord.stop(); } catch (Exception e) { Log.w(TAG, "AudioRecord stop", e); }
            audioRecord.release();
            audioRecord = null;
        }
        if (audioTrack != null) {
            try { audioTrack.stop(); } catch (Exception e) { Log.w(TAG, "AudioTrack stop", e); }
            audioTrack.release();
            audioTrack = null;
        }
    }
}
