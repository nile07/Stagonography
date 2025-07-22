from struct import pack, unpack  # ✅ Add this import

class Steganography:
    @staticmethod
    def encode_message(image_path, message, password, output_path):
        import cv2
        import numpy as np
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Random import get_random_bytes
        from Crypto.Util.Padding import pad

        salt = get_random_bytes(16)
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))

        # Payload: [4-byte length] + salt (16) + iv (16) + ciphertext
        raw_payload = salt + cipher.iv + ct_bytes
        length_prefix = pack('>I', len(raw_payload))  # 4-byte big-endian length
        full_payload = length_prefix + raw_payload

        binary_payload = ''.join(f"{byte:08b}" for byte in full_payload)

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or unsupported format")

        max_bytes = img.size // 8
        if len(full_payload) > max_bytes:
            raise ValueError("Message too large to encode in image")

        flat = img.flatten()
        for i in range(len(binary_payload)):
            flat[i] = np.uint8((int(flat[i]) & 0xFE) | int(binary_payload[i]))


        encoded = flat.reshape(img.shape)
        cv2.imwrite(output_path, encoded)

    @staticmethod
    def decode_message(image_path, password):
        import cv2
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Util.Padding import unpad

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or unsupported format")

        flat = img.flatten()
        binary = ''.join(str(byte & 1) for byte in flat)

        # Get first 32 bits = 4 bytes for length
        length_bits = binary[:32]
        length_bytes = bytes([int(length_bits[i:i+8], 2) for i in range(0, 32, 8)])
        payload_length = unpack('>I', length_bytes)[0]

        # Read only the payload
        payload_bits = binary[32:32 + (payload_length * 8)]
        if len(payload_bits) < payload_length * 8:
            raise ValueError("Corrupted image or truncated data")

        payload = bytes([int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8)])

        salt = payload[:16]
        iv = payload[16:32]
        ct = payload[32:]

        try:
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode()
        except (ValueError, UnicodeDecodeError):
            raise ValueError("Decryption failed: wrong password or corrupted image")

