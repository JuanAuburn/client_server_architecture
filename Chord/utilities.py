import hashlib


# cd C:\Users\Juano\Documents\Proyectos\client_server_architecture\FileServer

min_value = "00000000000000000000000000000000"
max_value = "ffffffffffffffffffffffffffffffff"
chunk_file = 10240000


def md5_for_string(string):
    hash_md5 = hashlib.md5()
    hash_md5.update(bytes(string, "utf8"))
    return hash_md5.hexdigest()


def md5_for_file(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def md5_for_data(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()


def hexa1_greater_than_hexa2(hexa1, hexa2):
    if len(hexa1) == len(hexa2):
        for x in range(len(hexa1)):
            if value_of_hexa_char(hexa1[x]) > value_of_hexa_char(hexa2[x]):
                return True
            elif value_of_hexa_char(hexa1[x]) < value_of_hexa_char(hexa2[x]):
                return False
        return False
    elif len(hexa1) > len(hexa2):
        return True
    else:
        return False


def hexa1_smaller_than_hexa2(hexa1, hexa2):
    if len(hexa1) == len(hexa2):
        for x in range(len(hexa1)):
            if value_of_hexa_char(hexa1[x]) < value_of_hexa_char(hexa2[x]):
                return True
            elif value_of_hexa_char(hexa1[x]) > value_of_hexa_char(hexa2[x]):
                return False
        return False
    elif len(hexa1) < len(hexa2):
        return True
    else:
        return False


def value_of_hexa_char(char):
    if char == "f" or char == "F":
        return 15
    elif char == "e" or char == "E":
        return 14
    elif char == "d" or char == "D":
        return 13
    elif char == "c" or char == "C":
        return 12
    elif char == "b" or char == "B":
        return 11
    elif char == "a" or char == "A":
        return 10
    elif char == "9":
        return 9
    elif char == "8":
        return 8
    elif char == "7":
        return 7
    elif char == "6":
        return 6
    elif char == "5":
        return 5
    elif char == "4":
        return 4
    elif char == "3":
        return 3
    elif char == "2":
        return 2
    elif char == "1":
        return 1
    else:
        return 0
