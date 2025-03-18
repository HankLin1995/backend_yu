from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PhotoBase(BaseModel):
    product_id: int
    file_path: str
    image_hash: str
    
    model_config = ConfigDict(from_attributes=True)

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    photo_id: int
    create_time: datetime
    
    model_config = ConfigDict(from_attributes=True)
