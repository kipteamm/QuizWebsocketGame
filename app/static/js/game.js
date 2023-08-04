function createPlayer(player, owner_id) {
    let creator = ''

    if (player.id == owner_id) {
        creator = ' (Creator)'
    }

    return `<div class="player" id="player-${player.id}">${player.username}${creator}</div>`
}


function updatePlayers(data) {
    const playerCount = document.getElementById('player-count');
    const playerList = document.getElementById('player-list');

    data.players.forEach(function(player) {
        playerList.appendChild(createPlayer(player, data.owner_id))
    })

    playerCount.innerText = data.player_count;

    if (data.player_count > 1) {
        const startGame = document.getElementById('start-game')

        startGame.style.display = 'block';
    }
}