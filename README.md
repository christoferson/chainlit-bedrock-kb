# chainlit-bedrock-kb
Chainlit Bedrock Knowledge Base


# Install

pip install --upgrade boto3
pip install -U langchain-community
pip install --upgrade chainlit
pip install --upgrade python-dotenv

# Install Test
chainlit hello

# Set Environment Variables (VsCode)
echo ${env:AWS_PROFILE}
$ENV:AWS_PROFILE = 'aws profile id'

# Launch

chainlit run app.py -h

# Links

- https://github.com/Chainlit/chainlit

- https://docs.chainlit.io/


# PIP3
pip freeze | findstr python-dotenv


# Docker
docker build .
docker run -d -p 8000:8000 --name bedrock-kb-container <image-id
docker exec -it bedrock-kb-container bash
docker logs bedrock-kb-container
docker exec -it bedrock-kb-container  /bin/bash

# Links

- https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html