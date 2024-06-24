def data_picker(body: dict):
    note_text = "TEST NOTE TEXT"#body["payload"]["Note"][0]["text"] if "text" in body["payload"]["Note"][0] else None
    created_time = body["payload"]["created_time"] if "created_time" in body["payload"] else None
    person_name = "TEST PERSON NAME" #body["payload"]["Note"][0]["person"]["name"] if "name" in body["payload"]["Note"][0][
        #"person"] else None
    cam_location = "TEST CAMERA LOCATION"#body["payload"]["cam_location"] if "cam_location" in body["payload"] else None
    issue_id = body["payload"]["Id"] 
    team_name = "TEST TEAM NAME"#body["payload"]["Team"]["name"] if "name" in body["payload"]["Team"] else None
    # cam_name = body["payload"]["cam_name"] if "cam_name" in body["payload"] else ""

    result = [issue_id, person_name, cam_location, created_time, team_name, note_text]

    return result


def data_picker_for_status_check(body: dict):
    completed_at = body["parameters"][2]["value"]
    solution = body["parameters"][3]["value"][3:] + " " + body["parameters"][4]["value"]
    sorted_data_for_status_check = [completed_at, solution]
    return sorted_data_for_status_check
