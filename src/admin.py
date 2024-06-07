# Здесь мы проверяем ID админов для сокращения общего кода в файле index
ID_ADMINUS1 = int(os.getenv('IDADMIN'))
ID_ADMINUS2 = int(os.getenv('IDADMIN2'))


def isAdmin(id):
    if id == ID_ADMINUS1 or ID_ADMINUS2:
        return True
    else:
        False