rule sms_metrics:
    input: 
        "data/raw/{pid}/messages_with_datetime.csv"
    params:
        sms_type = "{sms_type}",
        day_segment = "{day_segment}",
        metrics = lambda wildcards: config["SMS"]["METRICS"][wildcards.sms_type]
    output:
        "data/processed/{pid}/sms_{sms_type}_{day_segment}.csv"
    script:
        "../src/features/sms_metrics.R"

rule call_metrics:
    input: 
        "data/raw/{pid}/calls_with_datetime_unified.csv"
    params:
        call_type = "{call_type}",
        day_segment = "{day_segment}",
        metrics = lambda wildcards: config["CALLS"]["METRICS"][wildcards.call_type]
    output:
        "data/processed/{pid}/call_{call_type}_{day_segment}.csv"
    script:
        "../src/features/call_metrics.R"

rule battery_deltas:
    input:
        "data/raw/{pid}/battery_with_datetime.csv"
    output:
        "data/processed/{pid}/battery_deltas.csv"
    script:
        "../src/features/battery_deltas.R"

rule screen_deltas:
    input:
        "data/raw/{pid}/screen_with_datetime.csv"
    output:
        "data/processed/{pid}/screen_deltas.csv"
    script:
        "../src/features/screen_deltas.R"

rule google_activity_recognition_deltas:
    input:
        "data/raw/{pid}/plugin_google_activity_recognition_with_datetime.csv"
    output:
        "data/processed/{pid}/plugin_google_activity_recognition_deltas.csv"
    script:
        "../src/features/google_activity_recognition_deltas.R"

rule location_barnett_metrics:
    input:
        "data/raw/{pid}/locations_with_datetime.csv"
    params:
        accuracy_limit = config["BARNETT_LOCATION"]["ACCURACY_LIMIT"],
        timezone = config["BARNETT_LOCATION"]["TIMEZONE"]
    output:
        "data/processed/{pid}/location_barnett.csv"
    script:
        "../src/features/location_barnett_metrics.R"

rule bluetooth_metrics:
    input: 
        "data/raw/{pid}/bluetooth_with_datetime.csv"
    params:
        day_segment = "{day_segment}",
        metrics = config["BLUETOOTH"]["METRICS"]
    output:
        "data/processed/{pid}/bluetooth_{day_segment}.csv"
    script:
        "../src/features/bluetooth_metrics.R"
        
rule activity_metrics:
    input:
        gar_events = "data/raw/{pid}/plugin_google_activity_recognition_with_datetime.csv",
        gar_deltas = "data/processed/{pid}/plugin_google_activity_recognition_deltas.csv"
    params:
        segment = "{day_segment}",
        metrics = config["GOOGLE_ACTIVITY_RECOGNITION"]["METRICS"]
    output:
        "data/processed/{pid}/google_activity_recognition_{day_segment}.csv"
    script:
        "../src/features/google_activity_recognition.py"

rule battery_metrics:
    input:
        "data/processed/{pid}/battery_deltas.csv"
    params:
        day_segment = "{day_segment}",
        metrics = config["BATTERY"]["METRICS"]
    output:
        "data/processed/{pid}/battery_{day_segment}.csv"
    script:
        "../src/features/battery_metrics.py"

rule screen_metrics:
    input:
        screen_events = "data/raw/{pid}/screen_with_datetime.csv",
        screen_deltas = "data/processed/{pid}/screen_deltas.csv"
    params:
        day_segment = "{day_segment}",
        metrics_event = config["SCREEN"]["METRICS_EVENT"],
        metrics_deltas = config["SCREEN"]["METRICS_DELTAS"],
        episodes = config["SCREEN"]["EPISODES"]
    output:
        "data/processed/{pid}/screen_{day_segment}.csv"
    script:
        "../src/features/screen_metrics.py"

