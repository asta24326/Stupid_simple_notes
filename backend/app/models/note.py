from dataclasses import dataclass
from datetime import datetime

@dataclass
class Note:
    """ A Note as an application understands it
    This is the domain model: the service layer works only with Note objects,
    never with database rows or HTTP layers"""

    id: int
    text: str
    created_at: datetime
    
     