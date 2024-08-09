import pyaudio

def list_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    microphones = []
    for i in range(num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            microphones.append((i, device_info.get('name')))
    return microphones

def select_microphone():
    microphones = list_microphones()
    print("Available microphones:")
    for index, name in microphones:
        print(f"{index}: {name}")
    mic_index = int(input("Select the microphone index: "))
    return mic_index
