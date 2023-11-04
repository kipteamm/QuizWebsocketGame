let started = false;


function createPlayer(player, ownerID) {
    const playerElement = document.createElement('div')

    playerElement.classList.add('player')
    playerElement.id = `player-${player.user_id}`

    let creator = ''

    if (player.user_id == ownerID) {
        creator = ' (Creator)'
    }

    playerElement.innerHTML = player.username + creator + ` [${player.points}]`

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

    if (data.players.length > 1 && userID === data.owner_id && !started) {
        const startGame = document.getElementById('start-game')

        startGame.style.display = 'block';

        started = true
    }
}


const gameRoom = document.getElementById('game-room');


function startGame() {
    let seconds = 0;

    const interval = setInterval(() => {
        gameRoom.innerHTML = (5 - seconds);

        seconds++;

        if (seconds >= 5) {
            clearInterval(interval);
        }
    }, 1000);
}


function createQuestion(question) {
    const questionElement = document.createElement('form')
    
    questionElement.id = 'answer' 
    questionElement.method = "POST"
    questionElement.classList.add('question-wrapper')  

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


function question(question) {
    gameRoom.innerHTML = '';
    gameRoom.appendChild(createQuestion(question))

    answer = question.answer
}

function revealAnswer(answer) {
    document.querySelectorAll('input').forEach(element => {
        if (element.value !== answer) {
            element.style.display = 'none'
        }
    })
}