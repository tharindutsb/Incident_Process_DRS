from incident_process.incident_create import create_incident  # Note: Class name changed to PascalCase

if __name__ == "__main__":
    # Define the account number and incident ID
    account_num = "0000003746"
    incident_id = 9227534534

    # Create and process the incident in one step
    incident = create_incident(account_num, incident_id) 
    incident.process_incident()