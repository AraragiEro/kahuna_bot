import os
os.environ["KAHUNA_DB_DIR"] = r"F:\WorkSpace\GIT\kahuna_bot\AstrBot\data\plugins\kahuna_bot"

from .database import InvTypes, InvGroups, InvCategories
from .database import MetaGroups
from .database import IndustryActivityMaterials
from .database import IndustryActivityProducts
from .utils import SdeUtils