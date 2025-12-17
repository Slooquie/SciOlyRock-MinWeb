let allRockData = [];
let currentRock = null;
let isAnswerRevealed = false;

// DOM Elements
const rockImage = document.getElementById('rock-image');
const questionText = document.getElementById('question-text');
const userInput = document.getElementById('user-input');
const submitButton = document.getElementById('submit-button');
const revealButton = document.getElementById('reveal-button');
const hintButton = document.getElementById('hint-button');
const feedbackArea = document.getElementById('feedback-area');
const categoryFilter = document.getElementById('category-filter');
const gameMode = document.getElementById('game-mode');

// Initialization
async function init() {
    try {
        const response = await fetch('data/rocks_data.json');
        if (!response.ok) {
            throw new Error('Failed to load rock data');
        }
        allRockData = await response.json();
        console.log('Rock data loaded:', allRockData);

        populateCategories();
        loadNewCard();
    } catch (error) {
        console.error('Error initializing game:', error);
        feedbackArea.textContent = 'Error loading game data. Please refresh.';
        feedbackArea.className = 'incorrect';
    }
}

function populateCategories() {
    const categories = new Set(allRockData.map(r => r.category).filter(c => c));
    const sortedCategories = Array.from(categories).sort();

    sortedCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });
}

function loadNewCard() {
    if (allRockData.length === 0) return;

    // Filter logic
    const selectedCategory = categoryFilter.value;
    let filteredRocks = allRockData;
    if (selectedCategory !== 'all') {
        filteredRocks = allRockData.filter(r => r.category === selectedCategory);
    }

    if (filteredRocks.length === 0) {
        alert("No specimens found for this filter!");
        categoryFilter.value = 'all';
        filteredRocks = allRockData;
    }

    // Pick random
    const randomIndex = Math.floor(Math.random() * filteredRocks.length);
    currentRock = filteredRocks[randomIndex];

    // Reset State
    isAnswerRevealed = false;
    userInput.value = '';
    userInput.disabled = false;
    feedbackArea.textContent = '';
    feedbackArea.className = '';
    submitButton.disabled = false;
    hintButton.disabled = false;

    revealButton.textContent = 'Reveal Answer';

    // Update UI based on Mode
    const mode = gameMode.value;

    if (mode === 'category') {
        questionText.textContent = "Identify the Category!";
        userInput.placeholder = "Enter category (e.g. Igneous)...";
    } else if (mode === 'easy') {
        // Easy: Show Category, Guess Name
        questionText.innerHTML = `Identify the Specimen!<br><span style="font-size: 0.9em; font-weight: normal; color: #555;">(Category: ${currentRock.category})</span>`;
        userInput.placeholder = "Enter mineral/rock name...";
    } else {
        // Hard: Guess Name
        questionText.textContent = "Identify the Specimen!";
        userInput.placeholder = "Enter mineral/rock name...";
    }

    // Update Image
    rockImage.src = currentRock.image_url || 'placeholder.png';
    rockImage.alt = "Mystery Specimen";
}

function checkAnswer() {
    if (!currentRock || isAnswerRevealed) return;

    const guess = userInput.value.trim();
    if (!guess) return;

    const mode = gameMode.value;
    const normalizedGuess = guess.toLowerCase().replace(/\s+/g, ' ');
    let isCorrect = false;

    if (mode === 'category') {
        // Checking Category
        const normalizedCategory = (currentRock.category || "").toLowerCase().replace(/\s+/g, ' ');
        if (normalizedGuess === normalizedCategory) {
            isCorrect = true;
        }
    } else {
        // Checking Name (Easy or Hard)
        const normalizedName = (currentRock.common_name || "").toLowerCase().replace(/\s+/g, ' ');

        if (normalizedGuess === normalizedName) {
            isCorrect = true;
        }
    }

    if (isCorrect) {
        let successMsg = `✅ Correct! <br>Specimen: <strong>${currentRock.common_name}</strong>`;
        if (mode === 'category') {
            successMsg = `✅ Correct! It is <strong>${currentRock.category}</strong>.`;
        }

        feedbackArea.innerHTML = successMsg + `<br>Category: ${currentRock.category}<br><p>${currentRock.key_facts}</p>`;

        // Add source link if available
        if (currentRock.source_url) {
            feedbackArea.innerHTML += `<br><a href="${currentRock.source_url}" target="_blank" class="source-link" style="color: #3498db; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px;">View on Wikipedia ↗</a>`;
        }

        feedbackArea.className = 'correct';
        endRound();
    } else {
        feedbackArea.textContent = '❌ Incorrect. Try again or click Hint/Reveal.';
        feedbackArea.className = 'incorrect';
    }
}

function handleRevealClick() {
    if (isAnswerRevealed) {
        loadNewCard();
    } else {
        revealInformation();
    }
}

function revealInformation() {
    if (!currentRock) return;

    let sourceLinkHtml = "";
    if (currentRock.source_url) {
        sourceLinkHtml = `<br><a href="${currentRock.source_url}" target="_blank" class="source-link" style="color: #3498db; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px;">View on Wikipedia ↗</a>`;
    }

    feedbackArea.innerHTML = `<strong>Specimen:</strong> ${currentRock.common_name}<br>` +
        `<strong>Category:</strong> ${currentRock.category}<br>` +
        `<p>${currentRock.key_facts}</p>` +
        sourceLinkHtml;
    feedbackArea.className = 'revealed';

    endRound();
}

function giveHint() {
    if (!currentRock || isAnswerRevealed) return;

    const mode = gameMode.value;
    let hintText = "";

    if (mode === 'category') {
        hintText = `Hint: Category starts with '${currentRock.category.charAt(0)}'.`;
    } else if (mode === 'hard') {
        hintText = `Hint: It is a type of ${currentRock.category}.`;
    } else {
        hintText = `Hint: Starts with '${currentRock.common_name.charAt(0)}'.`;
    }

    feedbackArea.textContent = hintText;
    feedbackArea.className = 'revealed';
}

function endRound() {
    isAnswerRevealed = true;
    userInput.disabled = true;
    submitButton.disabled = true;
    hintButton.disabled = true;
    revealButton.textContent = 'Next Card';
}

// Event Listeners
submitButton.addEventListener('click', checkAnswer);
revealButton.addEventListener('click', handleRevealClick);
hintButton.addEventListener('click', giveHint);

categoryFilter.addEventListener('change', loadNewCard);
gameMode.addEventListener('change', loadNewCard);

userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        if (isAnswerRevealed) {
            loadNewCard();
        } else {
            checkAnswer();
        }
    }
});

window.addEventListener('DOMContentLoaded', init);
