ori = r"C:\Users\a\Documents\WeChat Files\wxid_ebrinpohxzm112\FileStorage\MsgAttach\d678cc1f0b6924b1b3ce87a6793f69e6\Image\2025-03\1bd53f7b1676eeb331f31bf7294acc40.dat"

with open(ori, 'rb') as f:
    file_head = f.read(20)

result = file_head
file_header_map = {
    b'\xff\xd8\xff': "jpg",
    b'\x89\x50\x4e\x47': 'png',
    b'\x47\x49\x46\x38': 'gif'
}


def bytes_xor(b1, b2, n_bytes):
    if n_bytes > len(b1) or n_bytes > len(b2):
        raise ValueError("n_bytes exceeds the length of one or both byte strings.")

    result = bytearray()

    for byte1, byte2 in zip(b1[:n_bytes], b2[:n_bytes]):
        # 对整个字节进行异或
        xor_result = byte1 ^ byte2
        result.append(xor_result)

    return bytes(result)


def bytes_all_equal(bytes):
    if len(bytes) < 1:
        return bytes
    first_byte = bytes[0]
    for b in bytes:
        if first_byte != b:
            return None
    return first_byte


def get_suffix(data):
    for header, suffix in file_header_map.items():
        header_len = len(header)
        s = bytes_xor(data[:header_len], header, header_len)
        eq_byte = bytes_all_equal(s)
        if eq_byte:
            ret_data = []
            with open(ori, 'rb') as r:
                ret_data = r.read()

            with open('./demo.' + suffix, 'wb') as f:
                for b in ret_data:
                    xor_result = b ^ eq_byte
                    f.write(xor_result.to_bytes(1, byteorder='big'))
            return suffix

    return None


print(get_suffix(result))
