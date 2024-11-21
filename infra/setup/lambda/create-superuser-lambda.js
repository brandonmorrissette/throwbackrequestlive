const AWS = require('aws-sdk');
const cognito = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
    const email = event.email;

    const params = {
        UserPoolId: process.env.USER_POOL_ID,
        Username: 'superuser',
        UserAttributes: [
            {
                Name: 'email',
                Value: email,
            },
        ],
    };

    try {
        const data = await cognito.adminCreateUser(params).promise();
        console.log('User created:', data);
        return {
            statusCode: 200,
            body: JSON.stringify(data),
        };
    } catch (error) {
        console.error('Error creating user:', error);
        return {
            statusCode: 500,
            body: JSON.stringify(error),
        };
    }
};
