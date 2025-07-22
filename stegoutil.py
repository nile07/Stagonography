import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class Steganography:
    @staticmethod
    def encrypt_message(image_path, message, password, output_path):
        """
        Encrypts a message using AES and embeds it into an image using LSB steganography.

        Args:
            image_path (str): Path to the original image.
            message (str): The plaintext message to hide.
            password (str): Password used for encryption.
            output_path (str): Path to save the encoded image.

        Raises:
            ValueError: If the image cannot store the encrypted message.
        """
        # AES Encryption
        salt = get_random_bytes(16)
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))

        # Payload: salt (16) + iv (16) + ciphertext
        payload = salt + cipher.iv + ct_bytes
        binary_payload = ''.join(f"{byte:08b}" for byte in payload)

        # Read and flatten image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or unsupported format")

        max_bytes = img.shape[0] * img.shape[1] * 3 // 8
        if len(payload) > max_bytes:
            raise ValueError("Message too large to encode in image")

        flat = img.flatten()
        for i in range(len(binary_payload)):
            flat[i] = (flat[i] & 0xFE) | int(binary_payload[i])
        encoded = flat.reshape(img.shape)

        cv2.imwrite(output_path, encoded)

    @staticmethod
    def decrypt_message(image_path, password):
        """
        Extracts and decrypts a hidden message from an image using the given password.

        Args:
            image_path (str): Path to the encoded (stego) image.
            password (str): Password used during encryption.

        Returns:
            str: Decrypted message.

        Raises:
            ValueError: If decryption fails or the password is wrong.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or unsupported format")

        flat = img.flatten()
        binary = ''.join(str(byte & 1) for byte in flat)
        payload_bytes = [int(binary[i:i+8], 2) for i in range(0, len(binary), 8)]
        payload = bytes(payload_bytes)

        if len(payload) < 32:
            raise ValueError("Invalid or missing encrypted data in image")

        salt = payload[:16]
        iv = payload[16:32]
        ct = payload[32:]

        try:
            key = PBKDF2(password, salt, dkLen=32, count=100000)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode()
        except (ValueError, UnicodeDecodeError) as e:
            raise ValueError("Decryption failed: wrong password or corrupted image")
