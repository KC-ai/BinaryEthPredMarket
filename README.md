# Binary ETH Prediction Market

A domain-specific language (DSL) and implementation for binary prediction markets on Ethereum.

## Project Structure

```
kc-ai-binaryethpredmarket/
├── README.md
├── Makefile            # Build and run pipeline
├── dsl/                # DSL implementation
│   ├── grammar.lark   # Lark grammar definition
│   ├── parser.py      # Parser implementation
│   └── example.dsl    # Example market definition
├── generator/         # Contract generation
│   ├── generator.py   # Main generator
│   └── templates/     # Solidity templates
├── sim/               # On-chain simulation
│   ├── contracts/     # Solidity contracts
│   │   ├── BinaryMarket.sol
│   │   └── GeneratedMarket.sol
│   ├── sim.js        # Hardhat test script
│   └── hardhat.config.js
├── analysis/         # Analysis tools
│   ├── data/         # Output data and figures
│   ├── single_run.py # Single market analysis
│   └── multi_run.py  # Multiple market analysis
└── requirements.txt  # Python dependencies
```

## Quick Start

Run the full pipeline:
```bash
make all
```

This runs the complete pipeline:
1. DSL parsing and contract generation
2. Hardhat tests
3. Market simulation
4. Analysis and visualization

## Manual Steps

If you prefer to run steps individually:

1. Install dependencies:
```bash
make install
```

2. Run tests:
```bash
make test
```

3. Run simulation:
```bash
make sim
```

4. Run analysis:
```bash
make analyze
```

5. Clean up:
```bash
make clean
```

## DSL Example

```dsl
market "Will ETH reach $5000 in 2024?"
oracle "0x123..."
fee 100
outcomes "Yes" "No"
mechanism "pooling"
```

## Analysis

The analysis tools provide:
- Reliability diagrams
- Expected Calibration Error (ECE)
- Brier scores
- Confidence intervals

Results are saved in the `analysis/data/` directory.
