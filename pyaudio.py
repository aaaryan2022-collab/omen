"""
PyAudio emulation layer powered by sounddevice.
Provides transparent PyAudio compatibility for Python 3.14+ on Windows.
"""

import sounddevice as sd

paFloat32 = 1
paInt32 = 2
paInt24 = 4
paInt16 = 8
paInt8 = 16
paUInt8 = 32
paCustomFormat = 65536

_FORMAT_MAP = {
    paFloat32: "float32",
    paInt32: "int32",
    paInt16: "int16",
    paInt8: "int8",
    paUInt8: "uint8",
}

_SAMPLE_SIZE = {
    paFloat32: 4,
    paInt32: 4,
    paInt16: 2,
    paInt8: 1,
    paUInt8: 1,
}


def get_sample_size(fmt):
    return _SAMPLE_SIZE.get(fmt, 2)


class Stream:
    def __init__(self, sd_stream):
        self._stream = sd_stream
        self._stopped = False

    def read(self, num_frames, exception_on_overflow=False):
        data, _overflow = self._stream.read(num_frames)
        return bytes(data)

    def write(self, data, exception_on_underflow=False):
        self._stream.write(data)

    def is_stopped(self):
        return self._stopped or getattr(self._stream, "stopped", False)

    def stop_stream(self):
        try:
            self._stream.stop()
        except Exception:
            pass
        self._stopped = True

    def start_stream(self):
        try:
            self._stream.start()
        except Exception:
            pass
        self._stopped = False

    def close(self):
        try:
            self._stream.close()
        except Exception:
            pass

    def is_active(self):
        return getattr(self._stream, "active", False)


class PyAudio:
    paFloat32 = paFloat32
    paInt32 = paInt32
    paInt24 = paInt24
    paInt16 = paInt16
    paInt8 = paInt8
    paUInt8 = paUInt8
    paCustomFormat = paCustomFormat

    def __init__(self):
        pass

    def terminate(self):
        pass

    def get_sample_size(self, fmt):
        return get_sample_size(fmt)

    def get_device_count(self):
        try:
            devices = sd.query_devices()
            return len(devices)
        except Exception:
            return 0

    def get_device_info_by_index(self, device_index):
        try:
            dev = sd.query_devices(device_index)
            return {
                "index": device_index,
                "name": dev.get("name", f"Device {device_index}"),
                "maxInputChannels": dev.get("max_input_channels", 0),
                "maxOutputChannels": dev.get("max_output_channels", 0),
                "defaultSampleRate": float(dev.get("default_samplerate", 16000.0)),
                "hostApi": dev.get("hostapi", 0),
            }
        except Exception as e:
            raise OSError(f"Invalid device index {device_index}: {e}")

    def get_default_input_device_info(self):
        try:
            default_idx = sd.default.device[0]
            if default_idx is None or default_idx < 0:
                devices = sd.query_devices()
                for i, dev in enumerate(devices):
                    if dev.get("max_input_channels", 0) > 0:
                        default_idx = i
                        break
            if default_idx is None or default_idx < 0:
                default_idx = 0
            return self.get_device_info_by_index(default_idx)
        except Exception:
            return {
                "index": 0,
                "name": "Default Microphone",
                "maxInputChannels": 1,
                "maxOutputChannels": 0,
                "defaultSampleRate": 16000.0,
                "hostApi": 0,
            }

    def get_default_output_device_info(self):
        try:
            default_idx = sd.default.device[1]
            if default_idx is None or default_idx < 0:
                devices = sd.query_devices()
                for i, dev in enumerate(devices):
                    if dev.get("max_output_channels", 0) > 0:
                        default_idx = i
                        break
            if default_idx is None or default_idx < 0:
                default_idx = 0
            return self.get_device_info_by_index(default_idx)
        except Exception:
            return {
                "index": 0,
                "name": "Default Speaker",
                "maxInputChannels": 0,
                "maxOutputChannels": 2,
                "defaultSampleRate": 44100.0,
                "hostApi": 0,
            }

    def open(self, *args, **kwargs):
        rate = kwargs.get("rate", 16000)
        channels = kwargs.get("channels", 1)
        fmt = kwargs.get("format", paInt16)
        dtype = _FORMAT_MAP.get(fmt, "int16")
        frames_per_buffer = kwargs.get("frames_per_buffer", 1024)
        input_flag = kwargs.get("input", False)
        output_flag = kwargs.get("output", False)
        input_device_index = kwargs.get("input_device_index", None)
        output_device_index = kwargs.get("output_device_index", None)

        if input_flag:
            stream = sd.RawInputStream(
                samplerate=rate,
                channels=channels,
                dtype=dtype,
                blocksize=frames_per_buffer,
                device=input_device_index,
            )
            stream.start()
            return Stream(stream)
        elif output_flag:
            stream = sd.RawOutputStream(
                samplerate=rate,
                channels=channels,
                dtype=dtype,
                blocksize=frames_per_buffer,
                device=output_device_index,
            )
            stream.start()
            return Stream(stream)
        else:
            raise ValueError("Must specify input=True or output=True")


__version__ = "0.2.14"
