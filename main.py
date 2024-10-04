import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def apply_deployments():
    """Apply the deployments and service YAML files."""
    
    print("Applying Chrome Node Deployment...")
    subprocess.run(["kubectl", "apply", "-f", "kubernetes/chrome_node.yaml"], check=True)

    print("Applying Test Controller Deployment...")
    subprocess.run(["kubectl", "apply", "-f", "kubernetes/test_controller.yaml"], check=True)

    print("Applying LoadBalancer Service...")
    subprocess.run(["kubectl", "apply", "-f", "kubernetes/chrome_node_service.yaml"], check=True)

    print("Deployments and services applied successfully.")

def scale_chrome_nodes(node_count):
    """Scale the Chrome Node deployment to the specified number of replicas."""
    
    print(f"Scaling Chrome Node deployment to {node_count} replicas...")
    subprocess.run(["kubectl", "scale", "deployment", "chrome-node", "--replicas", str(node_count)], check=True)
    print("Chrome Node deployment scaled successfully.")

def wait_for_pod_ready(label_selector, expected_count):
    """Wait for the specified pods to be in the 'Running' state based on a label selector."""
    
    print(f"Waiting for pods with label '{label_selector}' to be ready...")
    while True:
        # Get the status of pods matching the label selector
        result = subprocess.run(
            ["kubectl", "get", "pods", "-l", label_selector, "-o", "jsonpath={.items[*].status.phase}"],
            capture_output=True, text=True
        )
        phases = result.stdout.strip().split()
        
        # Check if we have the expected number of pods running
        running_count = sum(phase == "Running" for phase in phases)
        
        if running_count == expected_count:
            print(f"All {expected_count} pods with label '{label_selector}' are ready.")
            break
        elif result.returncode != 0:
            print(f"Error retrieving pod status: {result.stderr.strip()}")
            break
        time.sleep(5)

def run_test(chrome_node_index):
    """Run a single test in the Test Controller Pod for a specified Chrome Node."""
    
    pod_name = subprocess.run(
        ["kubectl", "get", "pods", "-l", "app=test-controller", "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True
    ).stdout.strip()

    print(f"Running test in Test Controller Pod {pod_name} for Chrome Node {chrome_node_index + 1}...")
    result = subprocess.run(["kubectl", "exec", pod_name, "--", "python", "test.py"], check=True)
    return f"Test for Chrome Node {chrome_node_index + 1} executed successfully." if result.returncode == 0 else f"Test for Chrome Node {chrome_node_index + 1} failed."

def run_tests(node_count):
    """Run tests for the specified number of Chrome Nodes in parallel."""
    
    with ThreadPoolExecutor(max_workers=node_count) as executor:
        futures = {executor.submit(run_test, i): i for i in range(node_count)}
        for future in as_completed(futures):
            chrome_node_index = futures[future]
            try:
                print(future.result())
            except Exception as e:
                print(f"Test for Chrome Node {chrome_node_index + 1} generated an exception: {e}")

def main():
    # Check for command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <node_count>")
        sys.exit(1)

    try:
        node_count = int(sys.argv[1])
    except ValueError:
        print("Error: node_count must be an integer.")
        sys.exit(1)

    # Apply deployments and services
    apply_deployments()

    # Scale the Chrome Node deployment
    scale_chrome_nodes(node_count)

    # Wait for the Test Controller Pods and Chrome Nodes to be ready
    wait_for_pod_ready("app=test-controller", 1)  # Assuming 1 Test Controller pod is expected
    wait_for_pod_ready("app=chrome-node", node_count)  # Wait for the expected number of Chrome nodes

    # Run tests in parallel
    run_tests(node_count)

    print("Deployment applied and tests executed.")

if __name__ == "__main__":
    main()
