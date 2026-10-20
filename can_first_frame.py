import can

def decode_temp(data):
    high_part = data[0] * 256     # left "wheel": each tick is worth 256
    low_part = data[1]            # right "wheel": 0 to 255
    raw = high_part + low_part    # the combined 16-bit number
    return raw / 10               # units of 0.1 °C, so divide by 10

bus_a = can.Bus(interface="virtual", channel="test")
bus_b = can.Bus(interface="virtual", channel="test")

# two fake BMS frames, both with the battery-temperature ID
msg1 = can.Message(arbitration_id=0x100, data=[0x01, 0xA4], is_extended_id=False)
msg2 = can.Message(arbitration_id=0x100, data=[0x02, 0x58], is_extended_id=False)

for msg in [msg1, msg2]:
    bus_a.send(msg)
    frame = bus_b.recv(timeout=1)
    temp = decode_temp(frame.data)
    print(f"ID {hex(frame.arbitration_id)}: Battery temperature {temp} °C")

bus_a.shutdown()
bus_b.shutdown()