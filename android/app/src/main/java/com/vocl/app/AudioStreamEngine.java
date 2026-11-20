package com.vocl.app;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.util.Log;

public final class AudioStreamEngine {

    private static final String TAG = "AudioStreamEngine";

    private static final int CAPTURE_RATE      = 16000;
    private static final int PLAYBACK_RATE     = 24000;
    private static final int CHANNEL_IN        = AudioFormat.CHANNEL_IN_MONO;
    private static final int CHANNEL_OUT       = AudioFormat.CHANNEL_OUT_MONO;
    private static final int ENCODING          = AudioFormat.ENCODING_PCM_16BIT;
    private static final int CHUNK_DURATION_MS = 100;

    // 16kHz * 2 bytes * 100ms = 3200 bytes per chunk
    public static final int CAPTURE_CHUNK_BYTES = CAPTURE_RATE * 2 * CHUNK_DURATION_MS / 1000;

    // Separate locks so blocking playback writes never stall mic capture reads
    private final Object captureLock  = new Object();
    private final Object playbackLock = new Object();

    private AudioRecord audioRecord;
    private AudioTrack  audioTrack;

    public void initCapture() {
        synchronized (captureLock) {
            releaseCaptureLocked();
            int minBuffer = AudioRecord.getMinBufferSize(CAPTURE_RATE, CHANNEL_IN, ENCODING);
            int bufferSize = Math.max(minBuffer * 2, 6400);
            // AudioSource.MIC avoids OEM HAL muting seen with VOICE_COMMUNICATION outside VoIP call mode
            audioRecord = new AudioRecord(
                    MediaRecorder.AudioSource.MIC,
                    CAPTURE_RATE, CHANNEL_IN, ENCODING, bufferSize);
            Log.i(TAG, "AudioRecord initialized: state=" + audioRecord.getState() + " buf=" + bufferSize);
        }
    }

    public void initPlayback() {
        synchronized (playbackLock) {
            releasePlaybackLocked();
            int minBuffer = AudioTrack.getMinBufferSize(PLAYBACK_RATE, CHANNEL_OUT, ENCODING);
            int bufferSize = Math.max(minBuffer * 2, 16384);
            AudioAttributes attrs = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build();
            AudioFormat format = new AudioFormat.Builder()
                    .setSampleRate(PLAYBACK_RATE)
                    .setChannelMask(CHANNEL_OUT)
                    .setEncoding(ENCODING)
                    .build();
            audioTrack = new AudioTrack(
                    attrs, format, bufferSize,
                    AudioTrack.MODE_STREAM, AudioManager.AUDIO_SESSION_ID_GENERATE);
            Log.i(TAG, "AudioTrack initialized: state=" + audioTrack.getState() + " buf=" + bufferSize);
        }
    }

    public void startCapture() {
        synchronized (captureLock) {
            if (audioRecord != null && audioRecord.getState() == AudioRecord.STATE_INITIALIZED) {
                audioRecord.startRecording();
            }
        }
    }

    public void restartCapture() {
        synchronized (captureLock) {
            Log.w(TAG, "Restarting AudioRecord after sustained zero-PCM reads");
            if (audioRecord != null && audioRecord.getState() == AudioRecord.STATE_INITIALIZED) {
                try {
                    if (audioRecord.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) {
                        audioRecord.stop();
                    }
                    audioRecord.startRecording();
                    return;
                } catch (Exception e) {
                    Log.w(TAG, "AudioRecord fast restart failed; re-initializing", e);
                }
            }
            initCapture();
            startCapture();
        }
    }

    public void startPlayback() {
        synchronized (playbackLock) {
            if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                audioTrack.play();
            }
        }
    }

    public byte[] readCaptureChunk() {
        AudioRecord record;
        synchronized (captureLock) {
            record = audioRecord;
        }
        if (record == null || record.getState() != AudioRecord.STATE_INITIALIZED) {
            return null;
        }
        byte[] buffer = new byte[CAPTURE_CHUNK_BYTES];
        int read = record.read(buffer, 0, buffer.length);
        if (read == buffer.length) {
            return buffer;
        }
        if (read > 0) {
            byte[] slice = new byte[read];
            System.arraycopy(buffer, 0, slice, 0, read);
            return slice;
        }
        return null;
    }

    public void writePlaybackData(byte[] pcmData) {
        synchronized (playbackLock) {
            if (audioTrack != null && audioTrack.getState() == AudioTrack.STATE_INITIALIZED) {
                audioTrack.write(pcmData, 0, pcmData.length, AudioTrack.WRITE_BLOCKING);
            }
        }
    }

    public void flushPlayback() {
        synchronized (playbackLock) {
            if (audioTrack == null || audioTrack.getState() != AudioTrack.STATE_INITIALIZED) return;
            audioTrack.pause();
            audioTrack.flush();
            audioTrack.play();
        }
    }

    public void release() {
        synchronized (captureLock) {
            releaseCaptureLocked();
        }
        synchronized (playbackLock) {
            releasePlaybackLocked();
        }
    }

    private void releaseCaptureLocked() {
        if (audioRecord != null) {
            try {
                if (audioRecord.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) {
                    audioRecord.stop();
                }
            } catch (Exception e) {
                Log.w(TAG, "AudioRecord stop", e);
            } finally {
                audioRecord.release();
                audioRecord = null;
            }
        }
    }

    private void releasePlaybackLocked() {
        if (audioTrack != null) {
            try {
                if (audioTrack.getPlayState() != AudioTrack.PLAYSTATE_STOPPED) {
                    audioTrack.stop();
                }
            } catch (Exception e) {
                Log.w(TAG, "AudioTrack stop", e);
            } finally {
                audioTrack.release();
                audioTrack = null;
            }
        }
    }
}
