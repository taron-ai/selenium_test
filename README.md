# Selenium Testing with Kubernetes

## Overview
This project implements a Selenium testing framework running on Kubernetes, utilizing a Test Controller Pod to manage test cases and a Chrome Node Pod for executing tests in a headless Chrome browser.

## System Architecture
- **Test Controller Pod**: Responsible for collecting and sending test cases to the Chrome Node Pods for execution.
- **Chrome Node Pod**: Runs the Selenium tests using the official Selenium Node Chrome image.

## How the Test Controller Pod Works
1. The Test Controller Pod reads the test cases defined in the `tests.py` file.
2. It communicates with the Chrome Node Pods using Kubernetes DNS.
3. It sends test requests to the Chrome Node Pods to execute the tests and waits for the results.

## Deployment Steps

### Prerequisites
- Ensure you have `kubectl` installed and configured.
- Ensure you have the AWS CLI installed and configured with your AWS credentials.

### Step 1: Set Up Amazon ECR
1. **Create an ECR Repository**:

   ```bash
   aws ecr create-repository --repository-name your_repository_name
   ```

2. **Authenticate Docker to Your ECR Registry**:

   #### From Local Machine

   ```bash
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your_account_id.dkr.ecr.your-region.amazonaws.com
   ```

   #### From EC2 Instance

   1. Connect to your EC2 instance.
   2. Install Docker if not already installed.
   3. Authenticate using the same command as above.

### Step 2: Build and Push Docker Images
1. **Build Docker Images**:

   ```bash
   docker build -t your_image_name .
   ```

2. **Tag the Images**:

   ```bash
   docker tag your_image_name:latest your_account_id.dkr.ecr.your-region.amazonaws.com/your_repository_name:latest
   ```

3. **Push the Images to ECR**:

   ```bash
   docker push your_account_id.dkr.ecr.your-region.amazonaws.com/your_repository_name:latest
   ```

### Step 3: Deploy to Kubernetes
1. **Apply Deployments**:

   ```bash
   kubectl apply -f test_controller_deployment.yaml
   kubectl apply -f chrome_node_deployment.yaml
   kubectl apply -f chrome_node_service.yaml
   ```

2. **Scale Chrome Node Deployment**:

   To scale the Chrome Node deployment based on the required number of nodes, use the following command:

   ```bash
   kubectl scale deployment chrome-node --replicas=<node_count>
   ```

   Replace `<node_count>` with the desired number of replicas.

3. **Check the Status of Pods**:

   ```bash
   kubectl get pods
   ```

4. **View Logs**:

   ```bash
   kubectl logs <pod_name>
   ```

## Inter-Pod Communication
- The Test Controller Pod communicates with the Chrome Node Pods using Kubernetes DNS.
- The Test Controller uses the service name of the Chrome Node Pods to send test execution requests.

## Running the Tests
Once the deployments are up and running, the Test Controller Pod will automatically start executing the test cases against the Chrome Node Pods.

### Command-Line Parameter
You can specify the number of Chrome Node replicas (for parallel testing) when running your test script:

```bash
python3 main.py <node_count>
```

Replace `<node_count>` with the desired number of Chrome Nodes to use for testing.

## Additional Notes
- Ensure your IAM user or role has the necessary permissions to push to ECR.
- If you're using EC2 instances, make sure they have the necessary IAM roles attached with permissions to access ECR.

## License
This project is licensed under the MIT License.
```
