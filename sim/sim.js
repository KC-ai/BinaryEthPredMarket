const { expect } = require("chai");
const { ethers } = require("hardhat");
const fs = require('fs');

describe("BinaryMarket", function () {
    let owner;
    let oracle;
    let bettors;
    const BET_AMOUNT = ethers.parseEther("0.1"); // 0.1 ETH per bet
    const NUM_SIMULATIONS = 50;
    const NUM_BETTORS = 10;
    const SIGNAL_PROB = 0.7; // Probability of Yes signal
    
    // Array to store simulation results
    let simulationResults = [];

    beforeEach(async function () {
        // Get signers - we need owner, oracle, and NUM_BETTORS bettors
        [owner, oracle, ...bettors] = await ethers.getSigners();
    });

    it("should simulate multiple markets with signal-based betting", async function () {
        console.log(`\nRunning ${NUM_SIMULATIONS} market simulations with ${NUM_BETTORS} bettors each...`);
        
        for (let i = 0; i < NUM_SIMULATIONS; i++) {
            // Deploy new contract for each simulation
            const BinaryMarket = await ethers.getContractFactory("contracts/Market1.sol:BinaryMarket");
            const market = await BinaryMarket.deploy(
                `Will ETH reach $5000 in 2024? (Sim ${i + 1})`,
                oracle.address,
                100  // 1% fee
            );
            await market.waitForDeployment();
            
            // Track signals and bets
            let yesSignals = 0;
            let noSignals = 0;
            
            // Have each bettor place a bet based on their signal
            for (let j = 0; j < NUM_BETTORS; j++) {
                const signal = Math.random() < SIGNAL_PROB;
                if (signal) {
                    await market.connect(bettors[j]).openPosition(0, { value: BET_AMOUNT }); // Yes
                    yesSignals++;
                } else {
                    await market.connect(bettors[j]).openPosition(1, { value: BET_AMOUNT }); // No
                    noSignals++;
                }
            }
            
            // Calculate majority signal
            const majorityYes = yesSignals > noSignals;
            
            // Resolve market based on majority signal
            await market.connect(oracle).resolveMarket(majorityYes ? 0 : 1);
            
            // Get final pool amounts and compute probability
            const [yesPool, noPool] = await market.getPools();
            const totalPool = yesPool + noPool;
            const pFinal = totalPool > 0 ? Number(yesPool) / Number(totalPool) : 0.5;
            
            // Store results
            simulationResults.push({
                run: i + 1,
                p_final: pFinal,
                outcome: majorityYes ? "1" : "0",
                yesSignals,
                noSignals,
                yesPool: ethers.formatEther(yesPool),
                noPool: ethers.formatEther(noPool)
            });
            
            if ((i + 1) % 10 === 0) {
                console.log(`Completed ${i + 1} simulations...`);
            }
        }
        
        // Save results to JSON file
        fs.writeFileSync(
            'final_probs.json',
            JSON.stringify(simulationResults, null, 2)
        );
        
        // Print summary
        console.log("\nSimulation Results Summary:");
        console.log(`Total simulations: ${simulationResults.length}`);
        console.log("\nSample entries:");
        for (let i = 0; i < 3; i++) {
            console.log(JSON.stringify(simulationResults[i], null, 2));
        }
        console.log("\nResults saved to final_probs.json");
        
        // Verify we have the expected number of simulations
        expect(simulationResults.length).to.equal(NUM_SIMULATIONS);
    });
}); 