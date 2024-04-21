/**
 * THIS FILE IS ONLY HERE FOR REVIEW PURPOSES. THIS CODE IS PRESENT IN THE AWS LAMBDA FUNCTION AND IT IS USED THERE.
 */

import { DynamoDB } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocument } from '@aws-sdk/lib-dynamodb';

const dynamo = DynamoDBDocument.from(new DynamoDB());

/**
 * Demonstrates a simple HTTP endpoint using API Gateway. You have full
 * access to the request and response payload, including headers and
 * status code.
 *
 * To scan a DynamoDB table, make a GET request with the TableName as a
 * query string parameter. To put, update, or delete an item, make a POST,
 * PUT, or DELETE request respectively, passing in the payload to the
 * DynamoDB API as a JSON body.
 */
export const handler = async (event) => {
    console.log('Received event:', JSON.stringify(event, null, 2));

    let tableName = event.headers.table_name;
    let body = "";
    let statusCode = "200";
    
    
    try {
        switch (event.httpMethod) {
            case 'GET':
                if (event.pathParameters === null) {
                    body = await dynamo.scan({TableName: tableName});
                    break;
                } else {
                    //https://dynobase.dev/dynamodb-errors/validationexception-invalid-keyconditionexpression-attribute-name-is-a-reserved-keyword/
                    body = await dynamo.query({
                        TableName: tableName,
                        ExpressionAttributeValues: {
                           ":uuid": event.pathParameters.userid
                        },
                        ExpressionAttributeNames: { "#lambda_uuid": "uuid" },
                        KeyConditionExpression: "#lambda_uuid = :uuid"
                    });
                    break;
                }
            case 'POST':
                body = await dynamo.update(JSON.parse(event.body));
                break;
            case 'PUT':
                body = await dynamo.put(JSON.parse(event.body));
                break;
            default:
                throw new Error(`Unsupported method "${event.httpMethod}"`);
        }
    } catch (err) {
        statusCode = '400';
        body = err.message;
    } finally {
        console.log(body);
        body = JSON.stringify(body);
        console.log(body);
    }

    return {
        statusCode,
        body
    };
};
