# BrainGameCenter

This project contains a demo of how data from the Shipley verbal test can be extracted and visualised
using Django, which is a web framework for creating database-driven websites in Python.

The project consists of two separate parts: experimental data emulation and analysis.

## Generating artificial data

We generate the artificial data in order to simulate an experiment on a number of participants (N=120).
Data emulation is shown in the file _artificial_data_generation.ipynb_ using the test sample of a real test taker.
_Average_ test sample from a real participant is stored in the file _Shipley_Trials.csv_. 
Demo version of the data analysis is stored in _EDA_for_web.ipynb_ file. This file allows to quickly view 
graphs in Jupyter Notebook without starting a web server.

   
## Visualising the data 

This part is handled by a Django application. When the web page with the data is requested,
an HTML template with placeholders for the graphs is loaded, along with the pre-processed data. 
The graphs are then generated using Plotly Express, and inserted into the template.
The result is then served to the client.

It should be noted that the data would ideally be stored in an SQL database for performance reasons.
But to keep the demo simple and to avoid an additional step, the web pages are generated dynamically
from the CSV files.

## List of dependencies

- python			3.11.9
- plotly express		5.22.0
- scipy			1.14.0
- Django			5.0.6
- numpy			2.0.0
- pandas			2.2.2
- py-irt			0.6.2


## Running the webserver

The django project can be tested locally without setting up a full web server by running the following command:
    
    python manage.py runserver

And then opening http://127.0.0.1:8000 in a web browser, as per the instructions in the output.

Note that on some systems, the python command will be called 'python3', and the local host IP can vary.


