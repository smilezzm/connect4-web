export default function ({ data, parentElement, setTriggerValue }) {
  const arena = parentElement.querySelector('.arena');
  const columns = arena.querySelector('.columns');
  const restart = arena.querySelector('.restart');
  const options = [...arena.querySelectorAll('input[name="first"]')];
  const heading = arena.querySelector('.status h2');
  const hint = arena.querySelector('.hint');
  const moveCount = arena.querySelector('.moves');
  const error = arena.querySelector('.error');
  const winning = new Set(data.winning.map(([row, column]) => `${row},${column}`));
  const listeners = new AbortController();
  const event = { signal: listeners.signal };
  let pending = false;

  if (!columns.children.length) {
    for (let column = 0; column < 7; column++) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'column';
      const number = document.createElement('span');
      number.className = 'col-number';
      number.textContent = column + 1;
      button.append(number);

      for (let row = 0; row < 6; row++) {
        const disc = document.createElement('span');
        disc.className = 'disc';
        disc.setAttribute('aria-hidden', 'true');
        button.append(disc);
      }
      columns.append(button);
    }
  }

  if (arena.dataset.first !== String(data.first)) {
    arena.dataset.first = data.first;
    for (const option of options) option.checked = Number(option.value) === data.first;
  }

  const buttons = [...columns.children];
  const animate = arena.dataset.revision !== String(data.revision);
  arena.dataset.revision = data.revision;

  function render(board, legal, last, moves, animateLast) {
    const names = { '-1': 'bot', 0: 'empty', 1: 'you' };
    buttons.forEach((button, column) => {
      const stack = board.map(row => row[column]);
      const description = stack.slice().reverse().filter(Boolean).map(piece => names[piece]).join(', ');
      button.setAttribute('aria-label', `Column ${column + 1}. ${description ? `From bottom: ${description}` : 'Empty'}`);
      button.setAttribute('aria-disabled', String(!legal.includes(column)));
      stack.forEach((piece, row) => {
        const disc = button.children[row + 1];
        const latest = last?.[0] === row && last[1] === column;
        disc.className = 'disc';
        disc.classList.toggle('human', piece === 1);
        disc.classList.toggle('bot', piece === -1);
        disc.classList.toggle('last', latest);
        disc.classList.toggle('arriving', latest && animateLast);
        disc.classList.toggle('winning', winning.has(`${row},${column}`));
      });
    });
    moveCount.textContent = `${moves} ${moves === 1 ? 'move' : 'moves'}`;
  }

  function submit(action) {
    pending = true;
    restart.disabled = true;
    for (const option of options) option.disabled = true;
    error.hidden = true;
    heading.textContent = 'AI bot is thinking…';
    hint.textContent = 'Waiting for its move.';
    setTriggerValue('action', { ...action, revision: data.revision });
  }

  function drop(column) {
    if (pending || !data.legal.includes(column)) return;
    const board = data.board.map(row => row.slice());
    const row = board.findLastIndex(cells => cells[column] === 0);
    board[row][column] = 1;
    render(board, [], [row, column], data.moves + 1, true);
    submit({ type: 'drop', column });
  }

  buttons.forEach((button, column) => button.addEventListener('click', () => drop(column), event));
  columns.addEventListener('keydown', e => {
    if (!e.altKey && !e.ctrlKey && !e.metaKey && /^[1-7]$/.test(e.key)) {
      e.preventDefault();
      drop(Number(e.key) - 1);
    }
  }, event);
  restart.addEventListener('click', () => {
    if (pending) return;
    for (const button of buttons) button.setAttribute('aria-disabled', 'true');
    const first = Number(options.find(option => option.checked).value);
    submit({ type: 'restart', first });
    if (first === 1) {
      heading.textContent = 'Starting a new game…';
      hint.textContent = '';
    }
  }, event);

  restart.disabled = false;
  for (const option of options) option.disabled = false;
  render(data.board, data.legal, data.last, data.moves, animate);
  const outcomes = {
    1: ['You win!', 'You connected four.'],
    '-1': ['AI bot wins', 'The bot connected four.'],
    0: ['Draw', 'The board is full.'],
  };
  const [title, detail] = outcomes[data.result] ?? ['Your turn', 'You play the gold discs.'];
  heading.textContent = title;
  hint.textContent = detail;
  error.textContent = data.error;
  error.hidden = !data.error;

  return () => listeners.abort();
}
