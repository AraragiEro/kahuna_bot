from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    db_dir: str = "."
    """数据库绝对路径"""
