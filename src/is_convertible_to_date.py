from datetime import datetime
def is_convertible_to_date(s, fmt="%d/%m/%Y"):
    try:
        datetime.strptime(s, fmt)
        return True
    except ValueError:
        return False