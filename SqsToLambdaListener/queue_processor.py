"""
script for running sqs listener
Originally created by Yaakov Gesher under Apache license
Original available at https://github.com/jegesh/python-sqs-listener
Modified portions released under MIT license
@author: Thomas Petersen
@version: 0.0.1
@license: Apache/MIT
"""

# ================
# start imports
# ================

import boto3
import json
import time
import logging
import os
import sys
import io

# ================
# start class
# ================

sqs_logger = logging.getLogger('sqs_listener')

class SqsToLambdaListener(object):

    def __init__(self, queueurl, lambdaarn, **kwargs):
        """
        :param queue: (str) name of queue to listen to
        :param kwargs: error_queue=None, interval=60, visibility_timeout='600', error_visibility_timeout='600', force_delete=False
        """
        self._queue_url = queueurl
        self._lambdaarn = lambdaarn
        self._region_name = kwargs['region_name'] if 'region_name' in kwargs else 'us-east-1'
        self._poll_interval = kwargs["interval"] if 'interval' in kwargs else 60
        self._message_attribute_names = kwargs['message_attribute_names'] if 'message_attribute_names' in kwargs else []
        self._attribute_names = kwargs['attribute_names'] if 'attribute_names' in kwargs else []
        self._force_delete = kwargs['force_delete'] if 'force_delete' in kwargs else False
        # must come last
        self._client = self._initialize_client()


    def _initialize_client(self):
        sqs = boto3.client('sqs', region_name=self._region_name)
        return sqs

    def _start_listening(self):
        # TODO consider incorporating output processing from here: https://github.com/debrouwere/sqs-antenna/blob/master/antenna/__init__.py
        while True:
            messages = self._client.receive_message(
                QueueUrl=self._queue_url,
                MessageAttributeNames=self._message_attribute_names,
                AttributeNames=self._attribute_names,
                WaitTimeSeconds = 20,
            )
            if 'Messages' in messages:
                sqs_logger.info( str(len(messages['Messages'])) + " messages received")
                for m in messages['Messages']:
                    receipt_handle = m['ReceiptHandle']
                    m_body = m['Body']
                    message_attribs = None
                    attribs = None

                    # catch problems with malformed JSON, usually a result of someone writing poor JSON directly in the AWS console
                    try:
                        params_dict = json.loads(m_body)
                    except:
                        sqs_logger.warning("Unable to parse message - JSON is not formatted properly")
                        continue
                    if 'MessageAttributes' in m:
                        message_attribs = m['MessageAttributes']
                    if 'Attributes' in m:
                        attribs = m['Attributes']
                    try:
                        def deletemsg():
                            self._client.delete_message(
                                QueueUrl=self._queue_url,
                                ReceiptHandle=receipt_handle
                            )
                        self.handle_message(deletemsg, params_dict, message_attribs, attribs)
                    except Exception as ex:
                        # need exception logtype to log stack trace
                        sqs_logger.exception(ex)
                        print(ex)

            else:
                time.sleep(self._poll_interval)

    def listen(self):
            sqs_logger.info( "Listening to queue " + self._queue_url)

            self._start_listening()

    def _prepare_logger(self):
        logger = logging.getLogger('eg_daemon')
        logger.setLevel(logging.INFO)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)

        formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
        formatter = logging.Formatter(formatstr)

        sh.setFormatter(formatter)
        logger.addHandler(sh)

    def handle_message(self, msgdeleter, body, attributes, messages_attributes):
        """
        Implement this method to do something with the SQS message contents
        :param body: dict
        :param attributes: dict
        :param messages_attributes: dict
        :return:
        """
        lbd = boto3.client('lambda', region_name=self._region_name)

        lbdresponse = lbd.invoke(
                FunctionName=self._lambdaarn,
                InvocationType='RequestResponse',
                Payload=json.dumps(body)
                )
        if lbdresponse['StatusCode'] in [200, 202] and not 'FunctionError' in lbdresponse:
            msgdeleter()
        else:
            # Should put in some loggin here
            pass
        return
