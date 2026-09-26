from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    #: 不齐顶加长开关；关闭时测算与改造前同参一致
    uneven_ceiling: bool = False
    #: 加长厘米；启用但留空（None）时取设置页维护的默认加长
    extra_cm: float | None = None
