from pydantic import BaseModel


class DefaultExtraCmRequest(BaseModel):
    #: 设置页维护的不齐顶默认加长厘米，必须为正数
    extra_cm: float
