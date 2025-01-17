## Setting Up the Hadoop Cluster Environment

1. **Generate an SSH Keypair**:
   - If you don't have an SSH keypair, generate one by running the following command on VM:

     ```bash
     ssh-keygen -t ed25519
     ```

   - Follow the prompts to create and save the keypair.

2. **Transfer Files to the Virtual Machine**:
   - Copy this folder to the VM where the setup will be performed.
   - Edit the `variables.tf` file to match the configuration of your VM.

3. **Build 5 Virtual Machines via Terraform**:
   - Initialise Terraform by running:

     ```bash
     terraform init
     ```
   - Apply the configuration to create the VMs:

     ```bash
     terraform apply
     ```
   - This will create 5 VMs:
     - 1 Host VM
     - 3 Worker VMs
     - 1 Storage VM

4. **Configure the Hadoop Cluster Environment via Ansible**:
   - Run the following command to set up the cluster environment:

     ```bash
     ansible-playbook -i generate_inventory.py full.yaml
     ```
   - This will configure the Hadoop cluster across the created VMs.
