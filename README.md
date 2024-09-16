<img src="./unnamed__1_.png" width=100%>

# RPS.ai
### Live web app: https://nilsdunlop.pythonanywhere.com (Not currently live)

## Concept
Rps.ai is an interactive version of the popular hand gesture game rock paper scissors, played by a human against a computer. Traditionally, the game is played by two players, with each player simultaneously showing their hand forming one of three possible hand shapes to the opponent, each shape representing either a rock, a paper or a pair of scissors. The rules dictate that rock wins over scissors, scissors win over paper, and paper wins over rock. The game has three possible outcomes for a player: a win, a loss, or a draw.

In the rps.ai website, the game is played by the system urging the user to play a hand shape in front of a web camera and responding with a randomly selected shape of one of the three hand shapes before declaring the outcome. This is done using an artificial neural network to determine the hand shape played by the user, and comparing it to the one played by the computer.

Rock paper scissors is not a truly random game due to human factors such as players utilizing psychological effects to exploit non-random behavior, something often noted during rock paper scissors tournaments. The goal of rps.ai is to eliminate these human non-random factors completely, making the experience of playing the game truly random, similar to that of a coin toss or a throw of dice.

## How to Use

### Locally

To clone and run this application locally, you need [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed on your computer.

#### Clone this repository
``` 
$ git clone https://github.com/NilsDunlop/RPS.git
```
#### Go into the repository
``` 
$ cd ai_project
```
#### Run server
``` 
$ python manage.py runserver
```

### Dockerized

To clone and run the application as a Dockerized application, you need [Docker](https://docs.docker.com/get-docker/) installed on your computer. 

#### Clone this repository
``` 
$ git clone https://github.com/NilsDunlop/RPS.git
```
#### Run server
``` 
$ docker-compose up
```
