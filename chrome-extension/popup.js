document.addEventListener('DOMContentLoaded', () => {
  const botStatus = document.getElementById('bot-status');
  const accountId = document.getElementById('account-id');
  const accountBalance = document.getElementById('account-balance');
  const signalsBody = document.getElementById('signals-body');
  const startBotBtn = document.getElementById('start-bot');
  const stopBotBtn = document.getElementById('stop-bot');

  // Mock data for demonstration purposes
  const mockAccountInfo = {
    connected: true,
    accountId: 'GX-12345',
    balance: '$10,000.00'
  };

  const mockSignals = [
    { symbol: 'EUR/USD', entry: 1.0750, target: 1.0800, stop_loss: 1.0720, confidence: 0.85 },
    { symbol: 'GBP/JPY', entry: 198.20, target: 199.00, stop_loss: 197.80, confidence: 0.78 },
    { symbol: 'XAU/USD', entry: 2350.00, target: 2360.00, stop_loss: 2345.00, confidence: 0.92 }
  ];

  function updateAccountInfo() {
    if (mockAccountInfo.connected) {
      botStatus.textContent = 'Connected';
      botStatus.className = 'status-connected';
      accountId.textContent = mockAccountInfo.accountId;
      accountBalance.textContent = mockAccountInfo.balance;
    } else {
      botStatus.textContent = 'Disconnected';
      botStatus.className = 'status-disconnected';
      accountId.textContent = 'N/A';
      accountBalance.textContent = 'N/A';
    }
  }

  function populateSignals() {
    signalsBody.innerHTML = ''; // Clear existing signals
    mockSignals.forEach(signal => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${signal.symbol}</td>
        <td>${signal.entry}</td>
        <td>${signal.target}</td>
        <td>${signal.stop_loss}</td>
        <td>${(signal.confidence * 100).toFixed(0)}%</td>
      `;
      signalsBody.appendChild(row);
    });
  }

  startBotBtn.addEventListener('click', () => {
    mockAccountInfo.connected = true;
    updateAccountInfo();
    console.log('Bot started');
  });

  stopBotBtn.addEventListener('click', () => {
    mockAccountInfo.connected = false;
    updateAccountInfo();
    console.log('Bot stopped');
  });

  // Initial population of data
  updateAccountInfo();
  populateSignals();
});
