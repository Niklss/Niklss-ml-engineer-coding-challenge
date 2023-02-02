# Coding Challenge

Welcome to the challenge! In this task you will get a glimpse into the typical challenges you would be facing working day to day within the Machine Translation team.

As a research engineer at Lengoo you will be creating and maintaning different services, supporting the machine translation automation and serving pipelines. This includes pre-processing data, creating and improving the performance of data microservices, defining deployment processes, as well as implementing and productionizing prototypes.

## I. Data Preprocessing Pipeline
The TMX (translation memory exchange) file format, a type of XML, is typical to the translation industry and contains previously translated sentences. It is one of the data sources that can be used in the machine translation model training process. A sample TMX file is provided under `resources/tmx-file.tmx`

As first part of the challenge, please implement a small pipeline for *extracting*, *cleaning* and *writing* the translated segments stored in the TMX file.
This should be completed in a scalable manner, considering large volumes of data.

### I.1 Extracting
Given a TMX file, parallel translated segments should be extracted and prepared for the next step.

### I.2 Cleaning
Typically, real historic translations from TMX files contain noise and artefacts from e.g. a content management system, so it is important to clean and extract the meaningful and contentful data before feeding it into the machine translation model.

* __Examples of non-clean segments__:
	* XML elements mid-segment:
		* `<seg>This segment <x/> is <g>great</g></seg>`
	* Escaped HTML tags mid-segment:
		* `<seg> This segment is &lt;br/&gt; great</seg>`
	* Other markup within text:
		* `<seg>This segment is %link_start%great%link_end%. </seg>`
	* Correct extraction in all cases:
		* "This segment is great."

Further noise may be discovered by empirical observation of the data. As this noise is always very customer-specific and can contain various, unpredictable elements, your code base should be easily extensible with further rules by using some neat code structures and interfaces.

### I.3 Writing
The queued segments are cleaned and utlimately written to any prefered parallel data structure/dump.

### I.4 Scaling
The same TMX preprocessing pipeline should be also runnable locally (RAM-limited) on a bigger data set. Your solution will be evaluated on the [ParaCrawl TMX files](https://object.pouta.csc.fi/OPUS-ParaCrawl/v1/tmx/de-en.tmx.gz), which contain 36.4M sentences. The priority for this step is performance and runnability, not the cleaning rules.

### Requirements
* __Functional Requirements__:
	* Command Line Interface (CLI)
	* Takes a TMX file and produces parallel file structure:
		* Example command: `$ python extract.py --tmx-file file.tmx --output “./myfolder/output”`
* __Expected Output__:
	* File object produced in `/myfolder`

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

