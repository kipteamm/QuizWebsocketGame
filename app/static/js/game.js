let started = false;


function createPlayer(player, ownerID) {
    const playerElement = document.createElement('div')

    playerElement.classList.add('player')
    playerElement.id = `player-${player.user_id}`

    let role = 'Player'

    if (player.user_id == ownerID) {
        role = 'Creator'
    }

    playerElement.innerHTML = `
        <div class="player-top">
            <span class="username">${player.username}</span>
            <span class="points">${player.points}</span>
        </div> 
        <p>
            (${role})
        </p>
    `

    return playerElement
}


function updatePlayer(playerElement, player) {
    const points = playerElement.querySelector('.points');
    const finalPoints = player.points;

    let initialPoints = parseInt(points.innerHTML, 10);
    
    let updatePointsAnimation = setInterval(updatePoints, 10);

    function updatePoints() {
        if (initialPoints >= finalPoints) {
            clearInterval(updatePointsAnimation);
            return;
        }

        points.innerHTML = `${++initialPoints}`;
    }
}


function updatePlayers(data, userID) {
    const playerCount = document.getElementById('player-count');
    const playerList = document.getElementById('player-list');

    data.players.forEach(function(player) {
        const playerElement = document.getElementById(`player-${player.user_id}`)

        if (playerElement === null) {
            playerList.appendChild(createPlayer(player, data.owner_id))
        } else {
            updatePlayer(playerElement, player)
        }
        
    })

    if (playerCount !== null) {
        playerCount.innerText = data.players.length;
    }
    
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
        gameRoom.innerHTML = `<span class="countdown">${(5 - seconds)}</span>`;

        seconds++;

        if (seconds >= 5) {
            clearInterval(interval);
        }
    }, 1000);
}


function createQuestion(question) {
    const questionElement = document.createElement('form')
    let answerElements = '';

    questionElement.id = 'answer' 
    questionElement.method = "POST"
    questionElement.classList.add('question-wrapper')  

    let answers = question.answers.sort((a, b) => 0.5 - Math.random());

    answers.forEach(answer => {
        answerElements += `<input type="submit" value="${answer}" class="answer">`
    })

    questionElement.innerHTML = `
        <div class="timer"></div>
        <p class="question">${question.question}</p>
        <div class="answers">
            ${answerElements}
        </div>
    `

    return questionElement
}


function question(question) {
    gameRoom.innerHTML = '';
    gameRoom.appendChild(createQuestion(question))
}


function playerAnswered(answer) {
    document.querySelectorAll('input.answer').forEach(element => {
        element.disabled = true;

        if (element.value === answer) {
            element.classList.add('user-answer')
        }
    })
}


function revealAnswer(answer) {
    document.querySelector('.timer').classList.add('paused')

    document.querySelectorAll('input.answer').forEach(element => {
        element.disabled = true;

        if (element.value === answer) {
            element.classList.add('correct')
        }
    })
}

function showWinner(data) {
    if (!data) return

    const player = document.getElementById(`player-${data.id}`);

    player.querySelector('.username').innerText = `${data.username} WINNER`;

    player.classList.add("active");
}