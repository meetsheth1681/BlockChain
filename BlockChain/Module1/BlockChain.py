# Create a BlockChain

import datetime                   #each blcok have its own timestamp at which it created
import hashlib                    #use for the hash of the block
import json                       #using Dom's function to encode the blocks before hashing
from flask import Flask,jsonify   #for web application


# Part 1 = Building of BlockChain--------->(Architecture of the BlockChain)

class BlockChain :
    def __init__(self) :          
            self.chain = []
            self.create_block( proof = 1 ,previous_hash = '0')
            
    #Creating BlockChain
        
    def create_block(self, proof ,previous_hash) :
        block = {'Index': len(self.chain) +1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash' : previous_hash,}
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
            
              
# Part 2 = Mining our BlockChain---------->

#creating a Web App

app = Flask(__name__)

#creating a BlockChain

blockchain = BlockChain()

# Mining a new block

@app.route('/mine_block', methods=['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash =blockchain.hash(previous_block)
    block = blockchain.create_block(proof,previous_hash)
    response = {'message':'Congratulation, you just create a block',
               'index':block['index'],
               'timestamp':block['timestamp'],
               'proof':block['proof'],
               'previous_hash':block['previous_hash']}
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
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'All good,The Blockchain is valid'}
    else:
        response = {'message' : 'Houston,ew have a problem.The Blockchain is invalid.'}
    return jsonify(response),200

#Running the app

app.run(host='0.0.0.0',port = 5000 )
