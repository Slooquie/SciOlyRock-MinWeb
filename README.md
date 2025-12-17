# SciOlyRock-MinWeb - Rocks & Minerals ID 🪨

A static web application designed to help students practice Rocks & Minerals identification for Science Olympiad. This project is a web-based adaptation of the [Minerobo Discord Bot](https://github.com/tctree333/Minerobo).

## Features

-   **Interactive Flashcards**: Test yourself on over 100 rocks and minerals.
-   **High-Quality Images**: Photos sourced from Wikipedia.
-   **Multiple Game Modes**:
    -   **Easy**: Identification with the Category (e.g., Igneous) provided as a hint.
    -   **Hard**: Pure specimen identification.
    -   **Training**: Practice identifying Rock Categories (Igneous, Metamorphic, etc.).
-   **Filtering**: Focus your study by filtering by Category.
-   **Hints & Sources**: Built-in hint system and direct links to Wikipedia for further reading.

## How to Play

1.  Visit the [live website](https://Slooquie.github.io/SciOlyRock-MinWeb/).
2.  Choose your **Game Mode** and **Filter** from the controls.
3.  Type your guess and hit Enter.

## Running Locally

1.  Clone the repository.
2.  Run the Python web server:
    ```bash
    python -m http.server
    ```
3.  Open `http://localhost:8000` in your browser.

## Data Generation

The data is generated using `fix_rocks.py`, which fetches the latest list from the Minerobo repo and retrieves high-resolution images from the Wikipedia API.
