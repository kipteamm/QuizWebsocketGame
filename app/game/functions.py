from typing import Optional

import datetime
import os


def user_object(user) -> dict:
    return {
        'user_id' : user.id,
        'username' : user.username,
        'victories' : user.victories,
        'games_played' : user.games_played
    }


def game_log(type: str, error: str, section: Optional[str]) -> None:
    if not section:
        section = "UNDEFINED"

    log = f"{type.upper()} - [{str(datetime.datetime.now())}] - {section.upper()} : {error}\n"

    log_file = open("game_log.txt", "a")

    log_file.write(log)
    log_file.close()

    return


def clear_game_log() -> None:
    os.remove("game_log.txt")

    return