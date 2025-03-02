import logging
import paramiko

from constants import VPS_IP, VPS_USER, VPS_PASSWORD

def ssh_connect():
    """Establish an SSH connection to the VPS."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASSWORD)
    return ssh


def ssh_execute(ssh, command):
    """Execute a command on the VPS via SSH and return the output."""
    logging.info(f'SSH Command: {command}')
    stdin, stdout, stderr = ssh.exec_command(command)
    output_lines = []
    
    for line in stdout:
        line = line.rstrip()
        logging.info(f'SSH Output: {line}')
        print(f'SSH Output: {line.encode("utf-8", "replace").decode("utf-8")}')
        output_lines.append(line)
    
    for line in stderr:
        line = line.rstrip()
        logging.error(f'SSH Error: {line}')
        print(f'SSH Error: {line.encode("utf-8", "replace").decode("utf-8")}')
        output_lines.append(line)
    
    output = '\n'.join(output_lines)
    logging.info(f'SSH Command Completed: {command}')
    return output