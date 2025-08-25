import ctypes, os

# Apple Silicon 默认路径
libpath = "/opt/homebrew/lib/libfluidsynth.dylib"
# Intel Mac 用 /usr/local/lib/libfluidsynth.dylib

fluidsynth = ctypes.CDLL(libpath)
print("Loaded FluidSynth from:", libpath)
