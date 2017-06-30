# SqsToLambdaListener
Very simple (too simple) class to invoke AWS lambdas with messages from Sqs

This is an edited version of the SQS lister at 
https://github.com/jegesh/python-sqs-listener/blob/master/setup.py

The use case is to carry messages off SQS queues and use them as payloads
against Lambda calls. I have used it mainly for interactive exploration
of the various types of error handling that are available in SQS and Lambda.

The key modifications are:
- A lot of code is removed 
- The handler is now specifically always an AWS Lambda call
- The listener now uses long polling (badly)
- You can't force delete messages any more

## Usage ##
Put the following in your requirements.txt
~~~~
-e git://github.com/CurryEleison/SqsToLambdaListener.git#egg=SqsToLamdaListener
~~~~
Then do a pip upgrade from the command line `pip install -r requirements.txt --upgrade`

Your code should look a bit like this

```python
from SqsToLambdaListener import SqsToLambdaListener

queueurl = 'https://sqs.[REGION].amazonaws.com/[ACCTID]/[QUEUENAME]'
lambdaarn = '[LAMBD_ARN]'
listener = SqsToLambdaListener(queueurl, lambdaarn, region_name='eu-west-1')
listener.listen()

```

