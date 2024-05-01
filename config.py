# Загальна довжина пакета із заголовком та CRC
DATA_LENGTH = 72

# Заголовок, 2 байти
HEADER_0 = b'\x7E'
HEADER_1 = b'\x7B'

# Шаблон розпакування даних
UNPACK_PATTERN = "<HHIHhhhhhhhhhffHffffffHhBBBBH"

# Поліном для розрахунку CRC
POLYNOMIAL = 0x1021
