import random
import string

def generate_group_code(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(characters, k=length))
