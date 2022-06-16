from pydantic import Extra, BaseSettings


class Config(BaseSettings):
    openid: str = ''

    class Config:
        extra = Extra.ignore
        case_sensitive = False
