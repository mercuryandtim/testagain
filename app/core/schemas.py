from pydantic import BaseModel
from typing import List, Optional, Union, Tuple
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Union[str, None] = None

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    branch_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    first_name: str
    surname: str
    email: str
    phone: str
    country: Optional[str] = None
    address: Optional[str] = None



class UserCreate(UserBase):
    password: str
    confirm_password: str

class User(UserBase):
    id: int
    is_active: bool
    # items: List[Item] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]
    is_active: Optional[bool]

    class Config:
        from_attributes = True
        
class BranchBase(BaseModel):
    name: str
    address: str

class BranchCreate(BranchBase):
    pass

class Branch(BranchBase):
    id: int
    items: List[Item] = []

    class Config:
        from_attributes = True


## classes for live.ai
class FileBase(BaseModel):
    key:str
    name:str
    
class AudioBase(FileBase):
   is_active: bool

class Audio(AudioBase):
   id: int
   owner_id: int
   class Config:
        from_attributes = True

class Avatar(FileBase):
    id:int
    owner_id: int
    class Config:
        from_attributes = True

class Background(FileBase):
    id:int
    owner_id: int
    class Config:
        from_attributes = True

class DataModel(BaseModel):
    key: str
    downloadUrl: str

class ResponseModel(BaseModel):
    data: DataModel

class AvatarModel(BaseModel):
    key: str

class BackgroundModel(BaseModel):
    key: str

class AudioModel(BaseModel):
    key: str

class VideoModel(BaseModel):
    avatar: AvatarModel
    background: BackgroundModel
    audio: AudioModel
    name: str 

class VideoInputModel(BaseModel):
    data: VideoModel

## Process Clip JSON structure

class Clip(BaseModel):
    file_path : str
    type : str
    has_audio: bool
    clip_size: Tuple[int, int]
    clip_position: Tuple[float, float]

class CompositeVideoRequest(BaseModel):
    output_size: Tuple[int, int]
    clips: List[Clip]

class VideoClips(BaseModel):
    clips_path: list[str]

## Front End JSON structure
from pydantic import BaseModel
from typing import List, Dict, Any

class Position(BaseModel):
    x:float
    y:float

class Size(BaseModel):
    width:float
    height:float

class Transform(BaseModel):
    position: Position
    size: Size

class Element(BaseModel):
    id: str
    name: str
    type: str
    url: str
    kind: str
    tag: str
    transform: Transform
    has_audio: bool

class Slide(BaseModel):
    name: str
    elements: List[Element]

class Project(BaseModel):
    name: str
    output_size: Tuple[int, int]
    slides: List[Slide]

class VoiceGeneratorConfig(BaseModel):
    key: str
    model: Dict[str, Any]
    stability: int
    similarityBoost: float
    style: float
    inputText: str

class ProjectData(BaseModel):
    user_id: int
    project: Project
    voiceGeneratorConfig: VoiceGeneratorConfig

class SyncRequest(BaseModel):
    project_data: ProjectData
    other_video_urls: List[str]

class AvatarSyncRequest(BaseModel):
    avatar_path: str
    audio_path: str
    current_user_id: int
    output_directory: str = None  # Optional output directory parameter
