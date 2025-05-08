from lark import Lark, Transformer

# Define the grammar
grammar = """
    start: market
    
    market: "market" string "{" fields "}"
    
    fields: outcomes
          oracle
          fee
          trading_mechanism
    
    outcomes: "outcomes:" "Yes" "," "No" ";"
    oracle: "oracle:" address ";"
    fee: "fee:" number "%" ";"
    trading_mechanism: "trading_mechanism:" "pool" ";"
    
    string: /"[^"]*"/
    address: /0x[0-9a-fA-F]{40}/
    number: /[0-9]+/
    
    %import common.WS
    %ignore WS
"""

# Create a transformer to convert the parse tree to a dictionary
class MarketTransformer(Transformer):
    def start(self, items):
        return items[0]
    
    def market(self, items):
        return {
            "question": items[0].strip('"'),
            "outcomes": items[1]["outcomes"],
            "oracle": items[1]["oracle"],
            "fee": items[1]["fee"],
            "mechanism": items[1]["mechanism"]
        }
    
    def fields(self, items):
        return {k: v for item in items for k, v in item.items()}
    
    def outcomes(self, _):
        return {"outcomes": ["Yes", "No"]}
    
    def oracle(self, items):
        return {"oracle": items[0]}
    
    def fee(self, items):
        return {"fee": int(items[0])}
    
    def trading_mechanism(self, _):
        return {"mechanism": "pool"}
    
    def string(self, items):
        return items[0]
    
    def address(self, items):
        return items[0]
    
    def number(self, items):
        return items[0]

def parse_market(text):
    parser = Lark.open('market_grammar.lark', parser='lalr', transformer=MarketTransformer())
    return parser.parse(text)

# Example usage
if __name__ == "__main__":
    example = '''
    market "Will ETH reach $5000 in 2024?" {
        outcomes: Yes, No;
        oracle: 0x1234567890123456789012345678901234567890;
        fee: 1%;
        trading_mechanism: pool;
    }
    '''
    
    result = parse_market(example)
    print(result) 