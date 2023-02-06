# Coding Challenge
## I. Data Preprocessing Pipeline
This preprocessing pipeline is made of lxml library for efficient file reading and multiprocessing to clear the data 
in parallel.  
After preprocessing the output file is stored in parquet format. This format was chosen mainly because 
of its read/write efficiency which is highly appreciate with large volumes of data.  
To run the code in local venv simply run this commands
```
pip install -r requirements.txt
python main.py --tmx-file ./resources/tmx-file.tmx --output ./results/output
```
It is also possible to pass a __processes__ argument. This argument stands for the amount of processes to run. By 
default this value equals to the amount of cpu available.  

It is also possible to run the code using docker. But you shouldn't forget about mounting the input and output files 
volumes.
```
docker build . -t test-cleaner
docker run --rm -it -v $PWD/resources:/opt/workspace/resources -v $PWD/results:/opt/workspace/results test-cleaner python main.py --tmx-file ./resources/tmx-file.tmx --output ./results/output
```
If you are interested in deeper code understanding look at the code. It has comments.
## II. Research and Prototyping

Misalignment, i.e., parallel sentence pairs that are not accurate translations of each other, is a common problem that occurs even in well-curated datasets.
In the second part of this challenge, you will be asked to extend your cleaning service with a cleaner that is able to identify and filter misaligned sentence pairs.
First, read and evaluate the following paper on [language agnostic sentence embeddings](https://arxiv.org/abs/1812.10464).
Make a prototypical cleaner implementation as a proposal on how to exploit sentence embeddings to filter misaligned segment pairs (see [Resources and Materials](https://github.com/lengoo/research-engineer-coding-challenge-template#resources-and-materials) for pre-trained sentence encoders).
Comment on the scalability and implementation requirements for productionizing your prototype.

### Requirements
* Implement a prototypical model-based cleaner using sentence embeddings
* Write a proposal on how to scale and productionize your prototype

## Resources and Materials
Below is a list of resources and materials that you might find useful for this challenge; however, please consider this list only as guidance and do not feel constrained to using necessarily these tools. We are interested in what you can come up with for this challenge.

* Extracting data from TMX files, `lxml`:
	* https://lxml.de/tutorial.html
* For queueing data into a pipeline, `RabbitMQ`:
	* https://www.rabbitmq.com/tutorials/tutorial-three-python.html
* For asynchronous data processing, `asyncio`:
	* https://docs.python.org/3/library/asyncio.html
* For asynchronous data processing over http, `aiohttp`:
	* https://aiohttp.readthedocs.io
* Pre-trained encoders for obtaining sentence embeddings:
	* https://github.com/facebookresearch/LASER


## Challange evaluation

1. Extensible, using standardizable formats
2. Clean, organized, and adhering to PEP8
3. Scalable to large data sets
4. With a clear readme and helpful documentation

