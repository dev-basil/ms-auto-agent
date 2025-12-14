About the project
-----------------

This project is a proof of concept for using LLMs to automatically resolve errors in microservices.

Steps to setup
--------------

1. Run the two books microservices(https://github.com/dev-basil/sample-microservices)
2. export groq api key export GROQ_API_KEY= 
3. install dependencies, pip install -r requirements.txt
4. uvicorn src.server:app --host 0.0.0.0 --port 8000

To run frontend (in frontend directory):

   npm i
   npm start

steps to run
------------
normal operation: 

curl http://localhost:3001/books/2   will return the book stock info. now stop the book-stock-service

docker stop book-stock-service

now try to get the book info again

curl http://localhost:3001/books/2

curl command will error out, check the frontend for error stream and approve the action



About the project
-----------------

This project is a proof of concept for using LLMs to automatically resolve errors in microservices.
