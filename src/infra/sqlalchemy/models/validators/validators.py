def is_char(value: str) -> str:
    if not value.isalpha():
        raise ValueError("Value must contain only alphabetic characters")
    return value

def is_digit(value: str) -> str:
    if not value.isdigit():
        raise ValueError("Value must contain only numeric characters")
    return value