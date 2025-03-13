from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    user_ids: list[int]
    webhook_url: str
    port: int

@dataclass
class Config:
    tg_bot: TgBot


def load_congig(path: str|None = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            user_ids=list(map(int, env.list('USER_IDS'))),
            webhook_url=env('WEBHOOK_URL'),
            port=int(env('PORT'))
        )
    )
