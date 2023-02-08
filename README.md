# Coding Challenge

## I. Data Preprocessing Pipeline

This preprocessing pipeline is made of lxml library (now I undertand it would be 
much more efficient just to read the file) for file reading and multiprocessing to 
clear the data in parallel.  
After preprocessing the output file is stored in parquet dataset format. 
This format was chosen mainly because of its read/write efficiency which is 
highly appreciate with large volumes of data.  

Basically, the code just splits the input file into chunks and start cleaning it in 
an asynchronous manner. It is possible to feed to the code a multicolumn data, the 
solution will handle it.  

To run the code in local venv simply run this commands

```
pip install -r requirements.txt
python tmx_preprocessing.py --tmx-file ./resources/tmx-file.tmx --output ./results/output
```

It is also possible to pass a __processes__ argument. This argument stands for 
the amount of processes to run. By default this value equals to the amount of 
cpu available. Also you can pass a __chunk-size__ argument. This argument stands 
for the amount of rows to pass to a process and the amount of rows stored in one 
dataset file.

It is also possible to run the code using docker. But you shouldn't forget about 
mounting the input and output file volumes. 

```
docker build . -t test-cleaner
docker run --rm -it -v $PWD/resources:/opt/workspace/resources -v $PWD/results:/opt/workspace/results test-cleaner python tmx_preprocessing.py --tmx-file ./resources/tmx-file.tmx --output ./results/output
```

If you are interested in deeper code understanding look at the code. It has comments.  

Tried to do my best, but it still requires about 5GB of RAM to process 20M rows. It 
is possible to get rid of memory leaking, but in this solution it strongly affects 
the performance.

## II. Research and Prototyping
For this part you are required to install some dependencies
```
fairseq==0.12.2
pytorch==1.13.1
```

In my opinion, if you have enough resources and you are more interested in a high 
quality result the LASER solution is not the best in case you are not working with 
too much languages. But since I'm limited in time I decided to try 
[the proposed solution](https://github.com/facebookresearch/LASER).  
Basically I just cloned the repository and used some of their API as long as a 
pretrained model.  

This prototype work on the parquet files produced by the first part of the challenge. 
Keep in mind it would be better to run the first code first =)  

The prototype consists of 4 parts:
1. Read the data from parquet file.
2. Iteratively calculate row embeddings and their cosine similarity.
3. Remove the rows from the data which thresholds are less than defined.
4. Write the resulting file.

To run the code localy firstly you install laser. Run this command in the root directory
```
bash install_laser.sh
```
To run the code use this command
```
python laser_cleaner.py --dataset-file ./results/output/output-0.parquet --output ./results/cleaned --limit 300
```
As with the first part it is also possible to run the solution in docker  
```
docker run --rm -it -v $PWD/results:/opt/workspace/results test-cleaner python laser_cleaner.py --dataset-file ./results/output/output-0.parquet --output ./results/cleaned --limit 300
```
This scripts accepts the parquet file or dataset folder. Understanding the slowness 
of the prototype it was decided to process only first file in dataset.  
As the output file it produces the parquet file, not dataset.  
Also due to speed limitations there exist __limit__ attribute. It stands for the 
amount of rows to process.  
And one of the most important attribute is __similarity-threshold__. It is floating 
point number from 0 to 1. This attribute decides whether the row will be 
eliminated or not. By default, defined 1.  

## Service proposal
In case I would need to build a service for MT large amount data clearing I would 
instead use a message broker like Kafka.  
Having one producer like tmx_preprocessing.py which splits the data into feasible 
parts and stores them in MinIO in parquet format. While splitting the data it also 
sends messages to the consumer via message broker with location (url) of chunk.  
Having multiple consumers they retrieve the message, download the chunk and process 
it. At the end they write a cleared dataset file into MinIO and write a message to 
message broker, signaling the success.  

Talking about MT dataset pairwise cleaning I would consider using DNN with pretrained 
source and target language models. Of course this model would be much more heavy than
proposed one, and need fine-tuning on a labeled dataset. But I'm 100% sure It will 
have at least twice less error rate.



