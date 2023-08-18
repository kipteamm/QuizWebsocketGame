function createPlayer(player, owner_id) {
    const playerElement = document.createElement('div')

    playerElement.classList.add('player')
    playerElement.id = `player-${player.user_id}`

    let creator = ''

    if (player.user_id == owner_id) {
        creator = ' (Creator)'
    }

    playerElement.innerHTML = player.username + creator

    return playerElement
}


function updatePlayers(data) {
    const playerCount = document.getElementById('player-count');
    const playerList = document.getElementById('player-list');

    playerList.innerHTML = '';

    data.players.forEach(function(player) {
        playerList.appendChild(createPlayer(player, data.owner_id))
    })

    playerCount.innerText = data.players.length();

    if (data.player_count > 1) {
        const startGame = document.getElementById('start-game')

        startGame.style.display = 'block';
    }
}