document.addEventListener('DOMContentLoaded', () => {
    const puzzleContainer = document.getElementById('puzzle');
    const shuffleButton = document.getElementById('shuffleButton');
    const helpButton = document.getElementById('helpButton');

    shuffleButton.addEventListener('click', shufflePuzzle);
    helpButton.addEventListener('click', getHelp);

    function shufflePuzzle() {
        fetch('/shuffle')
            .then(response => response.json())
            .then(data => renderPuzzle(data.puzzle));
    }

    function renderPuzzle(puzzle) {
        puzzleContainer.innerHTML = '';
        puzzle.forEach((row, rowIndex) => {
            row.forEach((tile, colIndex) => {
                const tileElement = document.createElement('div');
                tileElement.className = 'tile' + (tile === 0 ? ' empty' : '');
                tileElement.textContent = tile !== 0 ? tile : '';
                tileElement.addEventListener('click', () => moveTile(rowIndex, colIndex));
                puzzleContainer.appendChild(tileElement);
            });
        });
    }

    function moveTile(row, col) {
        fetch(`/move/${row}/${col}`)
            .then(response => response.json())
            .then(data => renderPuzzle(data.puzzle));
    }

    function getHelp() {
        alert("clicked")
        fetch('/help')
            .then(response => response.json())
            .then(data => {
                if (data.move) {
                    moveTile(data.move[0], data.move[1]);
                } else {
                    alert(data.error || 'No suggestion available');
                }
            });
    }

    // Initial shuffle on page load
    shufflePuzzle();
});
