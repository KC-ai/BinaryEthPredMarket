from market_parser import parse_market

def test_parser():
    with open('test_market.dsl', 'r') as f:
        market_text = f.read()
    
    result = parse_market(market_text)
    print("Parsed Market:")
    print(f"Question: {result['question']}")
    print(f"Outcomes: {result['outcomes']}")
    print(f"Oracle: {result['oracle']}")
    print(f"Fee: {result['fee']}%")
    print(f"Mechanism: {result['mechanism']}")

if __name__ == "__main__":
    test_parser() 