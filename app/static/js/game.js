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


function updatePlayers(data, userID) {
    const playerCount = document.getElementById('player-count');
    const playerList = document.getElementById('player-list');

    playerList.innerHTML = '';

    data.players.forEach(function(player) {
        playerList.appendChild(createPlayer(player, data.owner_id))
    })

    playerCount.innerText = data.players.length;

    if (data.players.length > 1 && userID === data.owner_id) {
        const startGame = document.getElementById('start-game')

        startGame.style.display = 'block';
    }
}


function createQuestion(question) {
    const questionElement = document.createElement('form')

    questionElement.classList.add('question-wrapper')
    questionElement.action = '#'
    questionElement.method = "POST"
    questionElement.id = 'question'   

    questionElement.innerHTML = `
        <span class="question">${question.question}</span>
    `

    const answers = question.incorrect_answers
    answers.push(question.correct_answer)

    answers.forEach(answer => {
        const answerElement = document.createElement('input')

        answerElement.type = 'submit'
        answerElement.value = answer

        questionElement.appendChild(answerElement)
    })

    return questionElement
}


const gameRoom = document.getElementById('game-room');

function question(question) {
    gameRoom.innerHTML = '';
    gameRoom.appendChild(createQuestion(question))
}