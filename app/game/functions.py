def user_object(user) -> dict:
    return {
        'user_id' : user.id,
        'username' : user.username,
        'victories' : user.victories,
        'games_played' : user.games_played
    }