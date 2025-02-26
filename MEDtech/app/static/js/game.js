let bpm = 117; // Default BPM for "I Will Survive"
let idealInterval = (60 / bpm) * 1000; // Interval in milliseconds
let lastClickTime = 0;
let score = 0;
let highScore = 0; // To track the highest score
let musicPlaying = false;
let isGameRunning = false; // To track if the game is active
let spawnInterval; // To store the interval for dot spawning

// Function to spawn a new dot
function spawnDot() {
    if (!isGameRunning) return; // Prevent spawning dots when the game is stopped

    const heartArea = document.getElementById("heart-area");
    const dot = document.createElement("div");
    dot.classList.add("dot");
    dot.style.top = "100%"; // Start position
    heartArea.appendChild(dot);

    // Animate the dot
    const dotAnimation = setInterval(() => {
        let top = parseFloat(dot.style.top);

        if (top <= 10) {
            // If the dot reaches the heart area
            clearInterval(dotAnimation);
            dot.remove();
        } else {
            dot.style.top = `${top - 2}%`; // Move the dot upward
        }
    }, 20); // Smooth animation

    // Remove dot after it exits the screen
    setTimeout(() => {
        if (dot.parentElement) {
            dot.remove();
        }
    }, 5000);
}

// Start spawning dots at the current BPM
function startGame() {
    if (isGameRunning) return; // Prevent multiple intervals

    isGameRunning = true;
    score = 0;
    updateScore();
    spawnInterval = setInterval(spawnDot, idealInterval);
    console.log("Game started");
}

// Stop the game and clear intervals
function stopGame() {
    if (!isGameRunning) return;

    isGameRunning = false;
    clearInterval(spawnInterval);
    updateHighScore();
    console.log("Game stopped");
}

// Function to evaluate the click pace
function checkTap() {
    if (!isGameRunning) return; // Ignore taps when the game is stopped

    checkClickPace(); // Evaluate the click pace
}

// Function to evaluate the click pace
function checkClickPace() {
    const currentTime = Date.now();
    const timeDiff = currentTime - lastClickTime;

    if (lastClickTime === 0) {
        // First click, no feedback yet
        displayFeedback("Click again to see pace!");
    } else {
        // Compare the time difference to the ideal interval
        if (timeDiff < idealInterval * 0.85) {
            displayFeedback("too-fast");
        } else if (timeDiff > idealInterval * 1.15) {
            displayFeedback("too-slow");
        } else {
            displayFeedback("amazing");
            score++;
            updateScore();
        }
    }

    // Update the last click time
    lastClickTime = currentTime;
}

// Update the high score
function updateHighScore() {
    if (score > highScore) {
        highScore = score;
        const highScoreDisplay = document.getElementById("high-score");
        highScoreDisplay.textContent = `High Score: ${highScore}`;
    }
}

// Display feedback
function displayFeedback(type) {
    const feedbacks = {
        "amazing": "Amazing Pace!",
        "too-fast": "Too Fast!",
        "too-slow": "Too Slow!",
        "Click again to see pace!": "Click again to see pace!"
    };

    // Hide all existing feedback
    Object.keys(feedbacks).forEach((key) => {
        const element = document.getElementById(key);
        if (element) {
            element.style.display = "none";
        }
    });

    // Display the feedback message
    const feedbackElement = document.getElementById(type);
    if (feedbackElement) {
        feedbackElement.style.display = "block";
    }
}

// Update the score
function updateScore() {
    const scoreDisplay = document.getElementById("score");
    scoreDisplay.textContent = `Score: ${score}`;
}

// Toggle music playback
function toggleMusic() {
    const audio = document.getElementById("background-music");

    if (!musicPlaying) {
        audio
            .play()
            .then(() => {
                console.log("Music started playing");
                musicPlaying = true;
            })
            .catch((error) => {
                console.error("Error playing music:", error);
            });
    } else {
        audio.pause();
        musicPlaying = false;
    }
}

// Function to change the song and BPM
function changeSong() {
    const audio = document.getElementById("background-music");
    const songSelector = document.getElementById("songs");
    const selectedSong = songSelector.value;

    // Update the audio source
    audio.src = `/static/audio/${selectedSong}`;
    audio.play();
    musicPlaying = true;

    // Update the BPM based on the selected song
    switch (selectedSong) {
        case "i_will_survive.mp3":
            bpm = 117;
            break;
        case "stayin_alive.mp3":
            bpm = 100;
            break;
        case "another_one_bites_the_dust.mp3":
            bpm = 110;
            break;
    }

    // Recalculate the ideal interval
    idealInterval = (60 / bpm) * 1000;

    // Restart dot spawning with the new BPM
    clearInterval(spawnInterval);
    if (isGameRunning) startGame();
}

// Initialize game
document.addEventListener("DOMContentLoaded", () => {
    updateScore();
});
