import hashlib


# cd C:\Users\Juano\Documents\Proyectos\client_server_architecture\FileServer


def md5_for_file(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
