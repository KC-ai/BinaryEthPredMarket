def generate_contract(market: dict) -> str:
    """Generate a Solidity contract from a market dictionary.
    
    Args:
        market: Dictionary containing market details with keys:
            - question: str
            - oracle: str (Ethereum address)
            - fee: int (basis points)
            - outcomes: list[str]
            - mechanism: str
    
    Returns:
        str: Complete Solidity contract source code
    """
    # Convert fee from percentage to basis points if needed
    fee = market['fee']
    if isinstance(fee, str) and fee.endswith('%'):
        fee = int(fee.rstrip('%')) * 100
    
    # Generate the contract source
    return f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Binary Market Contract
/// @notice A contract for creating and managing binary prediction markets
/// @dev Uses a pool-based mechanism for trading
contract BinaryMarket {{
    // Market state
    string public question;
    address public oracle;
    uint256 public fee;  // in basis points (1% = 100)
    string public mechanism;
    
    // Outcomes
    enum Outcome {{ Yes, No }}
    mapping(Outcome => uint256) public outcomeAmounts;
    
    // User positions
    mapping(address => mapping(Outcome => uint256)) public userPositions;
    
    // Market status
    bool public isResolved;
    Outcome public winningOutcome;
    
    // Events
    event MarketCreated(string question, address oracle, uint256 fee);
    event PositionOpened(address user, Outcome outcome, uint256 amount);
    event MarketResolved(Outcome winningOutcome);
    event WinningsClaimed(address user, uint256 amount);
    
    /// @notice Creates a new binary prediction market
    /// @param _question The question for the prediction market
    /// @param _oracle The address that can resolve the market
    /// @param _fee The fee in basis points (1% = 100)
    constructor(
        string memory _question,
        address _oracle,
        uint256 _fee
    ) {{
        require(_oracle != address(0), "Invalid oracle address");
        require(_fee <= 1000, "Fee too high"); // Max 10%
        
        question = _question;
        oracle = _oracle;
        fee = _fee;
        mechanism = "{market['mechanism']}";
        
        emit MarketCreated(_question, _oracle, _fee);
    }}
    
    /// @notice Opens a position in the market
    /// @param outcome The outcome to bet on (Yes or No)
    /// @dev Requires sending ETH with the transaction
    function openPosition(Outcome outcome) external payable {{
        require(!isResolved, "Market is resolved");
        require(msg.value > 0, "Must bet some ETH");
        
        // Update user position
        userPositions[msg.sender][outcome] += msg.value;
        
        // Update outcome amounts
        outcomeAmounts[outcome] += msg.value;
        
        emit PositionOpened(msg.sender, outcome, msg.value);
    }}
    
    /// @notice Resolves the market with the winning outcome
    /// @param _winningOutcome The winning outcome (Yes or No)
    /// @dev Only callable by the oracle
    function resolveMarket(Outcome _winningOutcome) external {{
        require(msg.sender == oracle, "Only oracle can resolve");
        require(!isResolved, "Market already resolved");
        
        isResolved = true;
        winningOutcome = _winningOutcome;
        
        emit MarketResolved(_winningOutcome);
    }}
    
    /// @notice Claims winnings for the caller
    /// @dev Calculates proportional share of the winning pool
    /// @return amount The amount of ETH claimed
    function claimWinnings() external returns (uint256 amount) {{
        require(isResolved, "Market not resolved");
        
        uint256 userAmount = userPositions[msg.sender][winningOutcome];
        require(userAmount > 0, "No winning position");
        
        // Calculate winnings with optimized math to avoid precision loss
        uint256 winningPool = outcomeAmounts[winningOutcome];
        
        // Calculate fee amount first
        uint256 feeAmount = (winningPool * fee) / 10000;
        uint256 netWinningPool = winningPool - feeAmount;
        
        // Calculate user's share using multiplication before division
        amount = (userAmount * netWinningPool) / outcomeAmounts[winningOutcome];
        
        // Clear user position
        userPositions[msg.sender][winningOutcome] = 0;
        
        // Transfer winnings
        (bool success, ) = msg.sender.call{{value: amount}}("");
        require(success, "Transfer failed");
        
        emit WinningsClaimed(msg.sender, amount);
    }}
}}'''

if __name__ == "__main__":
    # Example market from our DSL
    example_market = {
        "question": "Will ETH reach $5000 in 2024?",
        "oracle": "0x1234567890123456789012345678901234567890",
        "fee": 100,  # 1%
        "outcomes": ["Yes", "No"],
        "mechanism": "pool"
    }
    
    # Generate the contract
    contract_source = generate_contract(example_market)
    
    # Save to file
    with open("contracts/Market1.sol", "w") as f:
        f.write(contract_source)
    
    print("Generated contract saved to contracts/Market1.sol") 