from pydantic import BaseModel, EmailStr, computed_field


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


class ClothingItemCreate(BaseModel):
    name: str
    category: str


class ClothingItemResponse(BaseModel):
    id: int
    name: str
    category: str
    image_path: str
    user_id: int

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def image_url(self) -> str:
        return "/" + self.image_path


class OutfitCreate(BaseModel):
    name: str
    item_ids: list[int]


class OutfitResponse(BaseModel):
    id: int
    name: str
    user_id: int

    model_config = {"from_attributes": True}


class OutfitDetail(BaseModel):
    id: int
    name: str
    user_id: int
    items: list[ClothingItemResponse]

    model_config = {"from_attributes": True}
