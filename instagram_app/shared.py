from datetime import datetime 

def serialize_datetime(datetime: datetime): 
    return round(datetime.timestamp()) 