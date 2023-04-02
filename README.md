Code structure
==============
Used https://docs.python-guide.org/writing/structure/

Code conventions
================
Used [PEP-08](https://www.python.org/dev/peps/pep-0008/) and pylint


Instructions
============
Python version used: 3.8

1. __Recommended:__ create a virtual environment
    ```bash
    python3 -m venv ~/venv 
    ```
    Activate it
    ```bash
     source ~/venv/bin/activate 
    ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    python setup.py develop
    ```
3. Run tests
    ```bash
    python -m unittest discover
    ```
4. Run test coverage
    ```bash
    coverage run -m unittest discover
    ```
5. Run report
    ```bash
    coverage report -m
    ```
6. Run each step independently
    ```bash
    python flask_sqlalchemy_swagger/step_1.py
    ```
    ```bash
    python flask_sqlalchemy_swagger/step_2_3_4.py
    ```
 7 Go to http://localhost:8888/


Considerations
==============
 - Step 4 the UI Web is in interface of TomTom API is based on Swagger, used same approach for step 4.
 - Asynchronous tasks can be done either threads/processes or async event loop, I tried async and encounter this error [because flask is threaded](https://jdhao.github.io/2020/06/07/asyncio_inside_flask/)
 - Used sqlite3 in file for synchronization doesn't require install external dependencies.
 - Since it's a MVP, there are TODO comments in the code to implement:
    - Throttling or caching features to improve performance of incoming requests or external API requests.
    - Retry or limit quota for external API requests.
    - Fine grain tuning of handling exceptions and logging.
    - Not integration with WSGI or ASGI HTTP Server
    
