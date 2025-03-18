from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PhotoBase(BaseModel):
    ProductID: int
    FilePath: str
    ImageHash: str
    
    model_config = ConfigDict(from_attributes=True)

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    PhotoID: int
    CreateTime: datetime
    
    model_config = ConfigDict(from_attributes=True)
