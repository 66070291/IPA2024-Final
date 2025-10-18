#######################################################################################
# Yourname: Prem Lekphon
# Your student ID: 66070291
# Your GitHub Repo: https://github.com/66070291/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import netconf_final 
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")
MY_STUDENT_ID = "66070291"

if not ACCESS_TOKEN:
    raise Exception("WEBEX_ACCESS_TOKEN environment variable not set.")
if MY_STUDENT_ID.startswith("<!!!"):
    raise Exception("Please set MY_STUDENT_ID variable in the script.")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vN2FhMjYxMjAtYWMxOC0xMWYwLTk0YWItYjdjZWNhYzcxMWEz"
)

last_processed_message_id = None

while True:
    try:
        time.sleep(1)
        getParameters = {"roomId": roomIdToGetMessages, "max": 1}
        getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
        r = requests.get(
            "https://webexapis.com/v1/messages",
            params=getParameters,
            headers=getHTTPHeader,
        )
        
        if not r.status_code == 200:
            print(f"Error getting message from Webex: {r.status_code}")
            continue 

        # get the JSON formatted returned data
        json_data = r.json()

        if len(json_data["items"]) == 0:
            print("No messages in the room. Waiting...")
            continue 

        # store the array of messages
        messages = json_data["items"]
        
        current_message_id = messages[0]["id"]
        message = messages[0]["text"]
        
        if current_message_id == last_processed_message_id:

            continue
        print("Received message: " + message)
        
        last_processed_message_id = current_message_id


        # check if the text of the message starts with the magic character "/"
        if message.startswith(f"/{MY_STUDENT_ID} "):

            # extract the command
            try:
                command = message.split()[1]
                student_id = MY_STUDENT_ID
                print(f"Processing command: {command} for {student_id}")
            except IndexError:
                print("Message format error. Skipping.")
                continue

            
            # 5. Complete the logic for each command
            if command == "create":
                # First, check if the interface already exists
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status == "not_exist":
                    # Interface does not exist, proceed with creation
                    print(f"Interface does not exist. Attempting to create...")
                    
                    # Calculate IP address parts based on student ID
                    last_three_digits = student_id[-3:] 
                    ip_x = last_three_digits[0]         
                    ip_y = last_three_digits[1:]        
                    
                    # Call the create function from our netconf module
                    create_result = netconf_final.create(student_id, ip_x, ip_y)
                    
                    if create_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is created successfully"
                    else:
                        responseMessage = f"Error: Failed to create interface loopback {student_id}. Result: {create_result}"
                else:
                    # Interface already exists (status is up, down, or other)
                    print(f"Interface already exists (Status: {current_status}).")
                    responseMessage = f"Cannot create: Interface loopback {student_id}"    
            
            elif command == "delete":
                # 1. First, check if the interface already exists
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                # 2. If it exists (status is 'exists_up_up', 'exists_down_down', or 'exists_other')
                if current_status != "not_exist":
                    # Interface exists, proceed with deletion
                    print(f"Interface exists (Status: {current_status}). Attempting to delete...")
                    
                    # Call the delete function from our netconf module
                    delete_result = netconf_final.delete(student_id)
                    
                    if delete_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is deleted successfully"
                    else:
                        responseMessage = f"Error: Failed to delete interface loopback {student_id}. Result: {delete_result}"
                else:
                    # 3. Interface does not exist
                    print(f"Interface Loopback{student_id} does not exist.")
                    responseMessage = f"Cannot delete: Interface loopback {student_id}"
            
            elif command == "enable":
                # 1. First, check if the interface already exists
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                # 2. If it exists (status is 'exists_up_up', 'exists_down_down', or 'exists_other')
                if current_status != "not_exist":
                    # Interface exists, proceed with enabling it
                    print(f"Interface exists (Status: {current_status}). Attempting to enable...")
                    
                    # Call the enable function from our netconf module
                    enable_result = netconf_final.enable(student_id)
                    
                    if enable_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is enabled successfully"
                    else:
                        responseMessage = f"Error: Failed to enable interface loopback {student_id}. Result: {enable_result}"
                else:
                    # 3. Interface does not exist
                    print(f"Interface Loopback{student_id} does not exist.")
                    responseMessage = f"Cannot enable: Interface loopback {student_id}"
            
            elif command == "disable":
                # 1. First, check if the interface already exists
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                # 2. If it exists (status is 'exists_up_up', 'exists_down_down', or 'exists_other')
                if current_status != "not_exist":
                    # Interface exists, proceed with disabling it (shutdown)
                    print(f"Interface exists (Status: {current_status}). Attempting to disable...")
                    
                    # Call the disable function from our netconf module
                    disable_result = netconf_final.disable(student_id)
                    
                    if disable_result == "ok":
                        # Note: Using "shutdowned" as per the prompt's request
                        responseMessage = f"Interface loopback {student_id} is shutdowned successfully"
                    else:
                        responseMessage = f"Error: Failed to shutdown interface loopback {student_id}. Result: {disable_result}"
                else:
                    # 3. Interface does not exist
                    print(f"Interface Loopback{student_id} does not exist.")
                    # Note: Using "shutdown" as per the prompt's request
                    responseMessage = f"Cannot shutdown: Interface loopback {student_id}"
            
            elif command == "status":
                # 1. Call the status function from our netconf module
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                # 2. Map the result to the required response message
                if current_status == "exists_up_up":
                    # Condition: Exists and (admin=up, oper=up)
                    responseMessage = f"Interface loopback {student_id} is enabled"
                
                elif current_status == "exists_down_down":
                    # Condition: Exists and (admin=down, oper=down)
                    responseMessage = f"Interface loopback {student_id} is disabled"
                
                elif current_status == "not_exist":
                    # Condition: Does not exist
                    responseMessage = f"No Interface loopback {student_id}"
                
                else:
                    # Fallback for other states (e.g., "exists_other" which might be admin-up/oper-down)
                    responseMessage = f"Interface loopback {student_id} state is: {current_status}"
            
            # elif command == "gigabit_status":
            #    <!!!REPLACEME with code for gigabit_status command!!!>
            # elif command == "showrun":
            #    <!!!REPLACEME with code for showrun command!!!>
            else:
                responseMessage = "Error: No command or unknown command"
            
        # 6. Complete the code to post the message to the Webex Teams room.

            # if command == "showrun" and responseMessage == 'ok':
            #    ...
            
            # other commands only send text, or no attached file.
            # else: (ลบ else ออก เพราะตอนนี้ทุกคำสั่งจะส่งข้อความกลับ)
            
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            # Post the call to the Webex Teams message API.
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=postData,
                headers=HTTPHeaders,
            )
            
            if not r.status_code == 200:
                print(f"Error posting reply to Webex: {r.status_code}, {r.text}")
                continue
            
            print(f"Successfully posted response: {responseMessage}")
            
            response_json = r.json()
            last_processed_message_id = response_json["id"]

    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
        # (สามารถเพิ่มโค้ดส่ง Error นี้ไปที่ Webex ได้ ถ้าต้องการ)
        pass # แล้วรอ 1 วินาที (จาก time.sleep) แล้วเริ่มลูปใหม่