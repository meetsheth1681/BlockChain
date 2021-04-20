# Create a Cryptocurrency
#requests

import datetime                   #each blcok have its own timestamp at which it created
import hashlib                    #use for the hash of the block
import json                       #using Dom's function to encode the blocks before hashing
from flask import Flask,jsonify,request  
                                     #for web application and decentralize
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 = Building of BlockChain--------->(Architecture of the BlockChain)

class BlockChain :
    def __init__(self) :          
            self.chain = []
            self.transactions = []
            self.create_block( proof = 1 ,previous_hash = '0')
            self.nodes = set()
    #Creating BlockChain
        
    def create_block(self, proof ,previous_hash) :
        block = {'Index': len(self.chain) +1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash' : previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    #To know previous block's hash value
   
    def get_previous_block (self) :
        return self.chain[-1]
    
    #For checking that it is real or not
    
    def proof_of_work(self , previous_proof)  :
        new_proof = 1
        check_proof = False;
        while check_proof is False :
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]== '0000' :
                check_proof = True
            else:
                new_proof+=1
        return new_proof
    
    #The hash value of Block
    
    def hash(self,block) :
        encode_block = json.dumps(block,sort_keys = True).encode()
        return hashlib.sha256(encode_block).hexdigest()
    
    #Check it's hash with proof
    
    def is_chain_valid(self,chain):
        previous_block = chain [0]
        block_index = 1
        while block_index < len(chain) :
            block = chain[block_index]
            if block['previous_hash']!= self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]== '0000' :
                return True
            previous_block = block
            block_index +=1
        return True
    
    #adding transaction in BlockChain\
        
    def add_transactions(self,sender,receiver,amount) :
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block() 
        return previous_block['index'] + 1
    
    #Every node have to be updated with new transactions     
    
    def add_node(self , address) :
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self) :
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for nodes in network :
            response = requests.get(f'http://{nodes}/get_chain')
            if response.status_code == 200 :
                length = response.json()['length']
                chain = response.json()['chain']
                if len > max_length and self.is_chain_valid(chain) :
                    max_length = length
                    longest_chain = chain
        if longest_chain :
            self.chain = longest_chain
            return True
        return False
             
# Part 2 = Mining our BlockChain---------->

#creating a Web App

app = Flask(__name__)

#Creating an address for the node on Port 5000

node_address =  str(uuid4()).replace('-','')

#creating a BlockChain

blockchain = BlockChain()

# Mining a new block

@app.route('/mine_block', methods=['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash =blockchain.hash(previous_block)      
    blockchain.add_transactions(sender = node_address, receiver = 'RobinSharma', amount = 1 )
    block = blockchain.create_block(proof,previous_hash)
    response = {'message':'Congratulation, you just create a block',
               'index':block['index'],
               'timestamp':block['timestamp'],
               'proof':block['proof'],
               'previous_hash':block['previous_hash'],
               'transactions' :block['transactions'] }
    return jsonify(response),200   

#Creating the full BlockChain

@app.route('/get_chain', methods=['GET'])

def get_chain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response),200   

#Checking if the BlockChain id valid

@app.route('/is_valid', methods=['GET'])

def is_valid():
    is_chain_replace = blockchain.replace_chain()
    if is_chain_replace:
        response = {'message' : 'The node had different chains so the chain was replaced by the longest one.'}
    else:
        response = {'message' : 'Houston,ew have a problem.The Blockchain is invalid.'}
    return jsonify(response),200

# Adding new transaction to the Blockchain

@app.route('/add_transaction', methods=['POST'])

def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'some element of the tranaction are missing',400
    index = blockchain.add_transaction(json['sender'], json['receiver'],json ['amount'])
    response = {'message' : f'This transaction will be added {index}' }
    return jsonify(response), 201

# Part 3 = Decentralise System--------->

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None :
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are connnected.The Hadcoin Blockchian now contains the following nodes',
                       'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the largest chain if needed

@app.route('/replace_chain', methods=['GET'])

def replace_chain():
    is_replace_chain = blockchain.is_chain_valid(blockchain.chain)
    if is_replace_chain:
        response = {'message' : 'The node had different chains so the chian was replaced by the largest chain',
                    'new_chain' : blockchain.chain()}
    else:
        response = {'message' : 'All good.The chain was largest one ',
                    'actual_chain' : blockchain.chain}
    return jsonify(response),200
#Running the app

app.run(host='0.0.0.0',port = 5001 )

  