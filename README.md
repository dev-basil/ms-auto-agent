Steps to run
------------

1. Run the two books microservices
2. export groq api key export GROQ_API_KEY= 
3. run main.py
4. docker stop book-stock-service, then curl http://localhost:3001/books/2
    curl command will error out, but the agent will restart the book-stock-service
    following curls will succeed