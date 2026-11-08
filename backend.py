from snap7.type import Areas
from snap7.util import set_bool, get_bool
import snap7
import time
import cv2
import sys
import numpy as np
import os
from ultralytics import YOLO
import torch
from datetime import datetime
from frontend.utils.config import AppConfig
from frontend.utils.debug_logger import log_error, log_warning, log_info
import psutil

def set_priority_high():
    p = psutil.Process(os.getpid())
    if os.name == "nt":
        p.nice(psutil.HIGH_PRIORITY_CLASS)

def set_priority_above_normal():
    p = psutil.Process(os.getpid())
    if os.name == "nt":
        p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)

def set_priority_below_normal():
    p = psutil.Process(os.getpid())
    if os.name == "nt":
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

def configure_gpu_for_background():
    """Configure GPU to maintain performance when app loses focus"""
    if torch.cuda.is_available():
        try:
            torch.cuda.set_per_process_memory_fraction(0.99)
            
            torch.cuda.init()
            torch.cuda.synchronize()
            
            os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
            
        except Exception as e:
            print(f"⚠️ GPU configuration warning: {e}")

def get_size_thresholds_for_model(model_name_path, model_type='bf'):
    """
    Get size thresholds from database for filtering detections based on bounding box area.
    
    Args:
        model_name_path: Path of the model (e.g., 'Small_BF', 'Small_OD')
        model_type: 'bf' or 'od'
    
    Returns:
        dict: Dictionary with class names as keys and size threshold (px²) as values
              Example: {'rust': 1000, 'dent': 5000, 'damage': 3000}
              Returns empty dict {} if no thresholds found (will use 0 as default in filter)
    """
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=AppConfig.DB_HOST,
            user=AppConfig.DB_USER,
            password=AppConfig.DB_PASSWORD,
            database=AppConfig.DB_DATABASE
        )
        cursor = connection.cursor()
        
        table_name = 'bf_threshold_history' if model_type == 'bf' else 'od_threshold_history'
        
        query_model = f"SELECT model_name FROM {'bf_models' if model_type == 'bf' else 'od_models'} WHERE model_path = %s"
        cursor.execute(query_model, (model_name_path,))
        model_name_result = cursor.fetchone()
        model_name = model_name_result[0] if model_name_result else None

        if model_name:
            query = f"""
                SELECT size_threshold 
                FROM {table_name} 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """
            
            cursor.execute(query, (model_name,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result and result[0]:
                size_threshold_str = result[0]
                
                thresholds = {}
                
                pairs = size_threshold_str.split(', ')
                for pair in pairs:
                    if ':' in pair:
                        defect_name, threshold_str = pair.split(':')
                        threshold_value = int(threshold_str.strip())
                        thresholds[defect_name.strip()] = threshold_value
                
                return thresholds
            else:
                return {}
        else:
            return {}
            
    except Exception as e:
        print(f"❌ Error loading size thresholds from DB: {e}")
        import traceback
        traceback.print_exc()
        return {}
    
def get_thresholds_for_model(model_name_path, model_type='bf'):
    """
    Get thresholds from database in the format required by filter_detections.
    
    Args:
        model_name_path: Path of the model (e.g., 'Small_BF', 'Small_OD')
        model_type: 'bf' or 'od'
    
    Returns:
        dict: Dictionary with class names as keys and threshold percentages as values
              Example: {'rust': 80, 'dent': 90, 'damage': 75}
              Returns empty dict {} if no thresholds found (will use 50% default in filter)
    """
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=AppConfig.DB_HOST,
            user=AppConfig.DB_USER,
            password=AppConfig.DB_PASSWORD,
            database=AppConfig.DB_DATABASE
        )
        cursor = connection.cursor()
        
        table_name = 'bf_threshold_history' if model_type == 'bf' else 'od_threshold_history'
        
        query_model = f"SELECT model_name FROM {'bf_models' if model_type == 'bf' else 'od_models'} WHERE model_path = %s"
        cursor.execute(query_model, (model_name_path,))
        model_name_result = cursor.fetchone()
        model_name = model_name_result[0] if model_name_result else None

        if model_name:
            query = f"""
                SELECT defect_threshold 
                FROM {table_name} 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """
            
            cursor.execute(query, (model_name,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result and result[0]:
                defect_threshold_str = result[0]
                
                thresholds = {}
                
                pairs = defect_threshold_str.split(', ')
                for pair in pairs:
                    if ':' in pair:
                        defect_name, threshold_str = pair.split(':')
                        threshold_value = int(threshold_str.strip().rstrip('%'))
                        thresholds[defect_name.strip()] = threshold_value
                
                return thresholds
            else:
                return {}
        else:
            return {}
            
    except Exception as e:
        print(f"❌ Error loading thresholds from DB: {e}")
        import traceback
        traceback.print_exc()
        return {} 


def get_model_confidence_threshold(model_name_path, model_type='bf'):
    """
    Get the model confidence threshold from database.
    
    Args:
        model_name_path: Name of the model
        model_type: 'bf' or 'od'
    
    Returns:
        float: Model confidence threshold as decimal (e.g., 0.25 for 25%)
               Returns 0.25 (25%) as default if not found
    """
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=AppConfig.DB_HOST,
            user=AppConfig.DB_USER,
            password=AppConfig.DB_PASSWORD,
            database=AppConfig.DB_DATABASE
        )
        cursor = connection.cursor()
        
        table_name = 'bf_threshold_history' if model_type == 'bf' else 'od_threshold_history'
        
        query_model = f"SELECT model_name FROM {'bf_models' if model_type == 'bf' else 'od_models'} WHERE model_path = %s"
        cursor.execute(query_model, (model_name_path,))
        model_name_result = cursor.fetchone()
        model_name = model_name_result[0] if model_name_result else None

        if model_name:
            query = f"""
                SELECT model_threshold 
                FROM {table_name} 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """
            
            cursor.execute(query, (model_name,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                model_conf = float(result[0])
                return model_conf
            else:
                return 0.25
        else:
            return 0.25
            
    except Exception as e:
        print(f"❌ Error loading model confidence from DB: {e}")
        return 0.25

def get_roller_head_limits(roller_type):
    """
    Get high head and down head pixel limits from database for a specific roller type.
    
    Args:
        roller_type: Name of the roller type (e.g., "Small", "Medium", "Large")
    
    Returns:
        tuple: (high_head_pixels, down_head_pixels) or (180, 240) as default
    """
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host=AppConfig.DB_HOST,
            user=AppConfig.DB_USER,
            password=AppConfig.DB_PASSWORD,
            database=AppConfig.DB_DATABASE
        )
        cursor = connection.cursor()
        
        query = """
            SELECT high_head_pixels, down_head_pixels 
            FROM roller_data 
            WHERE roller_type = %s
        """
        
        cursor.execute(query, (roller_type,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            high_head = result[0] if result[0] is not None else 180
            down_head = result[1] if result[1] is not None else 240
            return high_head, down_head
        else:
            return 180, 240
            
    except Exception as e:
        print(f"❌ Error loading head limits from DB: {e}")
        return 180, 240

def annotate_detections(image, detections):
    """
    Draws bounding boxes and labels on the image using different colors per class.

    Args:
        image: Input image (numpy array).
        detections: list of tuples - (label, x1, y1, x2, y2, class_id, confidence)

    Returns:
        Annotated image (same shape as input).
    """
    COLORS = [
        (255, 255, 255),
        (0, 255, 255),
        (0, 255, 0),
        (255, 255, 0),
        (255, 0, 255),
        (255, 128, 0),
        (128, 255, 255),
        (255, 204, 229),
    ]


    font_scale = 0.7
    font_thickness = 2

    for det in detections:
        label, x1, y1, x2, y2, class_id, conf = det

        color = COLORS[class_id % len(COLORS)]

        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

        text = f"{label} {conf:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

        cv2.rectangle(image, (int(x1), int(y1) - text_height - 6),
                             (int(x1) + text_width + 2, int(y1)),
                             color, -1)

        cv2.putText(image, text, (int(x1), int(y1) - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)

    return image


def filter_detections(detections, confidence_thresholds, size_thresholds):
    """
    SIMPLIFIED: Filter detections using aligned thresholds
    
    detections: list of tuples - (label, x1, y1, x2, y2, class_id, confidence)
    class_names: list of class names indexed by class ID (not used since labels are already correct)
    thresholds: dict with class name as key and threshold as value (already aligned with model class names)
    """
    filtered = []
    
    for det in detections:
        label = det[0]
        x1, y1, x2, y2 = det[1:5]
        conf = det[6]
        
        
        conf_threshold_value = confidence_thresholds.get(label, 50)
        conf_threshold = conf_threshold_value / 100.0
        
        if conf < conf_threshold:
            continue

        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_area = bbox_width * bbox_height
        
        size_threshold = size_thresholds.get(label, 0)
        
        if bbox_area < size_threshold:
            continue
        
        filtered.append(det)

    return filtered

def plc_communication(plc_ip, rack, slot, db_number, shared_data, command_queue):
    """
    Handles all PLC communication: reading sensor statuses and executing commands.
    """
    set_priority_below_normal()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    plc_client = snap7.client.Client()
    try:
        plc_client.connect(plc_ip, rack, slot)
        log_info("inference", f"PLC connected successfully to {plc_ip}")
        print("✅ PLC Communication: Connected to PLC.")
        while True:
            if shared_data.get('bf_ready', False) and shared_data.get('od_ready', False):
                data = plc_client.read_area(Areas.DB, db_number, 0, 2)
                set_bool(data, byte_index=1, bool_index=6, value=True)
                set_bool(data, byte_index=1, bool_index=7, value=True)
                plc_client.write_area(Areas.DB, db_number, 0, data)
                shared_data['overall_system_ready'] = True
                plc_client.disconnect()
                break
        
    except Exception as e:
        print(f"PLC Communication: Connection error: {e} ⚠")
        shared_data["system_error"] = True
        return

    try:
        plc_client.connect(plc_ip, rack, slot)
        while True:
            data = plc_client.read_area(Areas.DB, db_number, 0, 3)


            shared_data['bigface_presence'] = get_bool(data, 0, 1)
            shared_data['bigface'] = get_bool(data, 0, 2)
            shared_data['od'] = get_bool(data, 0, 0)
            shared_data['od_presence'] = get_bool(data, 1, 4)
            shared_data['head_classification'] = get_bool(data, 2, 2)
            shared_data['system_mode'] = get_bool(data, 2, 0)
            shared_data['disc_status'] = get_bool(data, 2, 1)
            shared_data['system_ready'] = get_bool(data, 1, 6)

            while not command_queue.empty():
                command, _ = command_queue.get_nowait()
                if command == 'accept_bigface':
                    trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=0, action="accept")
                elif command == 'reject_bigface':
                    trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=1, action="reject")
                elif command == 'accept_od':
                    trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=2, action="accept")
                elif command == 'reject_od':
                    trigger_plc_action(plc_client, db_number, byte_index=1, bool_index=3, action="reject")
                else:
                    print(f"PLC Communication: Unknown command: {command}")

    except KeyboardInterrupt:
        data = plc_client.read_area(Areas.DB, db_number, 0, 2)  
        set_bool(data, byte_index=1, bool_index=6, value=False)  
        set_bool(data, byte_index=1, bool_index=7, value=False)  
        plc_client.write_area(Areas.DB, db_number, 0, data)

    except Exception as e:
        print(f"PLC Communication: Error during operation: {e} ⚠")
        log_error("inference", f"PLC connection failed to {plc_ip}", e)
        shared_data["system_error"] = True

    finally:
        plc_client.disconnect()
        print("✅ PLC Communication: Disconnected from PLC.")


def trigger_plc_action(plc_client, db_number, byte_index, bool_index, action):
    """Signal the PLC to perform an action (accept/reject)."""
    try:

        data = plc_client.read_area(Areas.DB, db_number, 0, 2)
        set_bool(data, byte_index=byte_index, bool_index=bool_index, value=True)
        plc_client.write_area(Areas.DB, db_number, 0, data)

        set_bool(data, byte_index=byte_index, bool_index=bool_index, value=False)
        plc_client.write_area(Areas.DB, db_number, 0, data)

    except Exception as e:
        print(f"⚠ PLC Action: Error triggering {action.upper()} slot: {e}")

def capture_frames_bigface(shared_frame_bigface, frame_lock_bigface, frame_shape, shared_data):
    """Continuously capture frames from the camera."""
    set_priority_above_normal()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)

    if not cap.isOpened():
        log_error("inference", "Failed to open BF camera")
        print("Failed to open camera.")
        sys.exit(1)

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                with frame_lock_bigface:
                    np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_frame, frame)
            else:
                log_error("inference", "Failed to capture frame from BF camera")
                print("Failed to capture frame.")
                shared_data["system_error"] = True
                time.sleep(0.1)
    except Exception as e:
        print(f"Camera capture error: {e}")
        shared_data["system_error"] = True


def process_rollers_bigface(shared_frame_bigface, frame_lock_bigface, roller_queue_bigface, model_bigface_path, proximity_count_bigface, roller_updation_dict, queue_lock, shared_data, frame_shape, shared_annotated_bigface, annotated_frame_lock_bigface):
    """Process frames for YOLO inference."""
    set_priority_high()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    detected_folder = f"C:\\Users\\{os.getlogin()}\\Desktop\\Inference\\BF\\Defect"
    os.makedirs(detected_folder, exist_ok=True)
    head_folder = f"C:\\Users\\{os.getlogin()}\\Desktop\\Inference\\BF\\Head_Defect"
    os.makedirs(head_folder, exist_ok=True)
    
    bf_triggered = False
    roller_dict = {}
    previous_head_status = False
     
    model_head_path = r".\models\BF_head.pt"

    try: 
        model_bf = YOLO(model_bigface_path)
        model_head = YOLO(model_head_path)
        if torch.cuda.is_available():
            model_bf.to("cuda")
            model_head.to("cuda")
            print("BF Model loaded in GPU")

            configure_gpu_for_background()
    except Exception as e:
        log_error("inference", "Failed to load BF model", e)
        print("Model is not loaded exiting process")
        return
        
    class_names = model_bf.names
    roller_class_index = 5
    
    defect_thresholds = get_thresholds_for_model(model_bigface_path, 'bf')
    model_conf_threshold = get_model_confidence_threshold(model_bigface_path, 'bf')
    size_thresholds = get_size_thresholds_for_model(model_bigface_path, 'bf')

    warmup_frame = r"Warmup BF.jpg"
    try:
        for i in range(30):
            results = model_bf.predict(warmup_frame, device=0, conf=1, verbose=False)
        print("Warmup image YOLO processing for bigface complete.")
        log_info("inference", "BF model warmup completed successfully")
        shared_data["bf_ready"] = True
    except Exception as e:
        log_error("inference", "BF model warmup failed", e)
        print(f"Error during YOLO inference on warmup image: {e}")

    try:
        for i in range(30):
            results = model_head.predict(warmup_frame, device=0, conf=0.5, verbose=False)
        log_info("inference", "Head classification model warmup completed") 
        print("Head Model Processed on Warmup Frame ")

    except Exception as e:
        log_error("inference", "Head classification model warmup failed", e)
        print(f"Error during head classification model inference: {e}")

    def point_inside(rectangle, list_of_all_rollers , roller_number):

        length = len(list_of_all_rollers)

        check = 2 if roller_number > 2 else roller_number

        if length > check:
            length =- 1

        roller_dictioanry = { i : list_of_all_rollers[idx] for idx,i in enumerate(range(roller_number , roller_number - length , -1)) }

        for idx,roller in roller_dictioanry.items():
            entire_coordinates = roller[1:5]    
            x1, y1 ,x2, y2  = [ int(i) for i in rectangle]
            decision = (entire_coordinates[0] <= x1 <= entire_coordinates[2] and entire_coordinates[1] <= y1 <= entire_coordinates[3]) or (entire_coordinates[0] <= x2 <= entire_coordinates[2] and entire_coordinates[1] <= y2 <= entire_coordinates[3])
            if decision:
                return idx
        return 0

    roller_id_counter = 0
    previous_bf_state = False

    selected_roller_type = shared_data.get('selected_roller_type', None)
    
    if selected_roller_type:
        latest_min, latest_max = get_roller_head_limits(selected_roller_type)
    else:
        latest_min, latest_max = 180, 240

    
    shared_data["bf_inspected"] = 0
    shared_data["bf_ok_rollers"] = 0
    shared_data["bf_not_ok_rollers"] = 0
    shared_data["bf_rust"] = 0
    shared_data["bf_dent"] = 0
    shared_data["bf_damage"] = 0
    shared_data["bf_high_head"] = 0
    shared_data["bf_down_head"] = 0
    shared_data["bf_others"] = 0

    allow_all = shared_data.get("allow_all", False)  
    if allow_all:
        allow_all_folder_bf = f"C:\\Users\\{os.getlogin()}\\Desktop\\All Frames\\BF\\All_BF"
        os.makedirs(allow_all_folder_bf, exist_ok=True)
        allow_all_folder_head = f"C:\\Users\\{os.getlogin()}\\Desktop\\All Frames\\BF\\All_Head"
        os.makedirs(allow_all_folder_head, exist_ok=True) 
    
    bf_file_counter = 0
    head_file_counter = 0
    bf_all_file_counter = 0
    head_all_file_counter = 0

    try:
        while True:
            
            current_bf_state = shared_data["bigface_presence"]

            if current_bf_state and not previous_bf_state:
                roller_id_counter += 1

                bf_triggered = True
                roller_dict[roller_id_counter] = {'defect': False , 'defect_names': ["No defect"]}
                shared_data["bf_inspected"] += 1
                log_info("inference", f"BF roller detected. Assigned Roller ID: {roller_id_counter}")
                print(f"\n🎯 BF New roller detected! Assigned Roller ID: {roller_id_counter}")

            current_head_state = shared_data["head_classification"]

            if current_head_state and not previous_head_status:

                with frame_lock_bigface:
                    np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    frame = np_frame.copy()

                results = model_head.predict(frame, device=0, conf=0.7, verbose=False, half=True, agnostic_nms=True)

                boxes = results[0].boxes.xyxy.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()

                x1r, y1r, x2r, y2r = 0, 0, 0, 0
                x1d, y1d, x2d, y2d = 0, 0, 0, 0 
                for (x1,y1,x2,y2),cls in zip(boxes,classes):
                    if cls == 0:
                        x1d, y1d, x2d, y2d = x1, y1, x2, y2
                    elif cls == 1:
                        x1r, y1r, x2r, y2r = x1, y1, x2, y2


                horizontal_distance = ( (x2r - x1r) - (x2d - x1d) )/2
                vertical_distance = ( (y2r - y1r) - (y2d - y1d) )/2

                distance_pixels = (horizontal_distance + vertical_distance)/2

                if distance_pixels < latest_min:
                    head_type = "High Head"
                elif distance_pixels > latest_max:
                    head_type = "Down Head"
                else:
                    head_type = "Normal"

                log_info("inference", f"HEAD TYPE: {head_type}, Roller ID: {roller_id_counter}")
                print(f"HEAD TYPE: {head_type}, Roller ID: {roller_id_counter}")
                if head_type == "High Head" or head_type == "Down Head":
                    data = roller_dict[roller_id_counter]["defect"] | True
                    defect_names = roller_dict[roller_id_counter]['defect_names'] + [head_type]
                    roller_dict[roller_id_counter] = {'defect': data, 'defect_names': defect_names}

                    annotated_frame = results[0].plot()

                    roller_text = f"Roller Id : {roller_id_counter}"
                    head_type_text = f"Head Type : {head_type}"
                    distance_text = f"Distance : {distance_pixels:.2f}mm"

                    cv2.putText(annotated_frame, roller_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, head_type_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, distance_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    annotated_frame = results[0].plot()
                    head_file_counter += 1
                    save_path = f"{head_folder}/{head_file_counter}.jpg"
                    cv2.imwrite(save_path, annotated_frame)

                    if allow_all:
                        head_all_file_counter += 1
                        allow_all_path = f"{allow_all_folder_head}/{head_all_file_counter}.jpg"
                        cv2.imwrite(allow_all_path, annotated_frame)
        

            previous_head_status = current_head_state

            if bf_triggered:
                with frame_lock_bigface:
                    np_frame = np.frombuffer(shared_frame_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    frame = np_frame.copy()


                results = model_bf.predict(frame, device=0, conf=model_conf_threshold, verbose=False, half=True, agnostic_nms=True)

                if roller_class_index is None:
                    return
                

                detections = []
                if results and results[0].boxes.data is not None:
                    for box in results[0].boxes.data:
                        x1, y1, x2, y2, conf, cls = box 
                        cls = int(cls)
                        label = "roller" if cls == roller_class_index else class_names[cls]
                        detections.append((label, int(x1), int(y1), int(x2), int(y2), cls, float(conf)))

                filtered_detections = filter_detections(detections, defect_thresholds, size_thresholds)
                detections = sorted(filtered_detections, key=lambda x: x[1])
                annotated_frame = frame.copy()
                annotated_frame = annotate_detections(annotated_frame, filtered_detections)
            
                
                has_roller_detection = any(detection[0] == "roller" for detection in detections)
                has_defect_detection = any(detection[0] != "roller" for detection in detections)

                if allow_all and has_roller_detection:
                    bf_all_file_counter += 1
                    allow_all_path = f"{allow_all_folder_bf}/{bf_all_file_counter}.jpg"
                    cv2.imwrite(allow_all_path, annotated_frame)            
                if has_roller_detection and has_defect_detection:
                    bf_file_counter += 1
                    save_path = f"{detected_folder}/{bf_file_counter}.jpg"
                    cv2.imwrite(save_path, annotated_frame)

                with annotated_frame_lock_bigface:
                    np_annotated = np.frombuffer(shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)
                    
                if len(detections) > 0:

                    roller_only_sorted = [detection for detection in detections if detection[0] == "roller" and detection[-1] > 0.80]
                    defect_only_sorted = [detection for detection in detections if detection[0] != "roller"]


                    for detection in defect_only_sorted:
                        roller_id = point_inside(detection[1:5] , roller_only_sorted , roller_id_counter)

                        if roller_id == 0:
                            continue

                        defect_detected =  False if roller_id == 0 else True

                        defect_name = "No Defect" if not defect_detected else class_names[detection[5]]

                        if roller_id in roller_dict:
                            data = roller_dict[roller_id]["defect"] | defect_detected
                            defect_names = roller_dict[roller_id]['defect_names'] + [defect_name]
                            roller_dict[roller_id] = {'defect': data, 'defect_names': defect_names}
                        else:
                            roller_dict[roller_id] = {'defect': defect_detected, 'defect_names': [defect_name]}
        

                if shared_data['od_presence'] and not OD_PRESENCE and len(roller_dict) > 0:
                    
                    OD_PRESENCE = True 

                    first_key = next(iter(roller_dict))
                    defect_detected = roller_dict[first_key]["defect"]
                    defect_names = roller_dict[first_key]['defect_names']

                    if first_key in roller_dict:
                        roller_data = roller_dict[first_key]
                        defect_detected = roller_data['defect']
                        defect_names = roller_data['defect_names']

                        if defect_detected:
                            log_info("inference", f"Defect detected for Roller ID: {first_key}")
                            shared_data["bf_not_ok_rollers"] += 1
                        else:
                            log_info("inference", f"No defect for Roller ID: {first_key}")
                            shared_data["bf_ok_rollers"] += 1
                            if shared_data.get("od_inspected") is not None:
                                shared_data["od_inspected"] += 1

                        unique_defects = set(defect_names)

                        for defect_name in unique_defects:
                            defect_lower = defect_name.lower()
                            
                            if defect_lower == "rust":
                                shared_data["bf_rust"] += 1
                            elif defect_lower == "dent":
                                shared_data["bf_dent"] += 1
                            elif defect_lower == "damage":
                                shared_data["bf_damage"] += 1
                            elif defect_lower == "high head":
                                shared_data["bf_high_head"] += 1
                            elif defect_lower == "down head":
                                shared_data["bf_down_head"] += 1
                            elif defect_lower != "no defect":
                                shared_data["bf_others"] += 1

                    roller_queue_bigface.put(defect_detected)
                    roller_updation_dict[first_key] = int(defect_detected)
                    roller_dict.pop(first_key)

                elif not shared_data['od_presence']:
                    OD_PRESENCE = False  
                    
            previous_bf_state = current_bf_state

    except Exception as e:
        log_error("inference", "Error in BF roller processing", e)
        print(f"BF Roller Processing Error: {e}")
        shared_data["system_error"] = True
        

def handle_slot_control_bigface(roller_queue_bigface,shared_data,command_queue):
    """Control slot mechanism based on second proximity sensor."""
    set_priority_below_normal()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    global roller_number

    try:
        a = False
        while True:
            if shared_data["bigface"] and not a:
                a = True
                if not roller_queue_bigface.empty():
                    defect_detected = roller_queue_bigface.get()
                    status = "Defective" if defect_detected else "Good"
                    command_queue.put(("accept_bigface" if not defect_detected else "reject_bigface", None))
            elif not shared_data["bigface"]:
                a = False
    except Exception as e:
        print(f"Slot Control Error: {e}")
        log_error("inference", "Error in slot control", e)
        shared_data["system_error"] = True

def capture_frames_od(shared_frame_od, frame_lock_od, frame_shape, shared_data):
    """Continuously capture frames from the camera."""
    set_priority_above_normal()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')
    
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_shape[1])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_shape[0])

    if not cap.isOpened():
        log_error("inference", "Failed to open OD camera")
        print("Failed to open camera.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, -1)
                with frame_lock_od:
                    np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_frame, frame)
            else:
                log_error("inference", "Failed to capture frame from OD camera")
                print("Failed to capture frame.")
                shared_data["system_error"] = True
                time.sleep(0.01)
    except Exception as e:
        print(f"Camera capture error: {e}")
        shared_data["system_error"] = True

def process_frames_od(shared_frame_od, frame_lock_od, roller_queue_od, model_od_path, queue_lock, shared_data, frame_shape, roller_updation_dict,shared_annotated_od, annotated_frame_lock_od):
    """Process frames for YOLO inference and track roller defects with pulse debounce & proper exit handling."""
    set_priority_high()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    detected_folder = f"C:\\Users\\{os.getlogin()}\\Desktop\\Inference\\OD\\Defect"
    os.makedirs(detected_folder, exist_ok=True)

    def point_inside(rectangle, list_of_all_rollers , roller_number):
        
        length = len(list_of_all_rollers)

        check = 3 if roller_number > 3 else roller_number

        if length > check:
            length =- 1

        roller_dictioanry = { i : list_of_all_rollers[idx] for idx,i in enumerate(range(roller_number , roller_number - length , -1)) }

        for idx,roller in roller_dictioanry.items():
            entire_coordinates = roller[1:5]    
            x1, y1 ,x2, y2  = [ int(i) for i in rectangle]
            decision = (entire_coordinates[0] <= x1 <= entire_coordinates[2] and entire_coordinates[1] <= y1 <= entire_coordinates[3]) or (entire_coordinates[0] <= x2 <= entire_coordinates[2] and entire_coordinates[1] <= y2 <= entire_coordinates[3])
            if decision:
                return idx
        return 0

    try:

        od_model = YOLO(model_od_path).to("cuda")
        print("OD Model loaded in GPU")
        configure_gpu_for_background()
    except Exception as e:
        log_error("inference", "Failed to load OD model", e)
        print("Model is not loaded exiting process")
        return

    warmup_frame = r"Warmup OD.jpg"
    try:
        for i in range(30):
            od_model.predict(warmup_frame, device=0, conf=0.2, verbose=False)
        print("Warmup image YOLO processing for od complete.")
        log_info("inference", "Warmup image YOLO processing for od complete.")
        shared_data["od_ready"] = True
    except Exception as e:
        print(f"Error during YOLO inference on warmup image: {e}")
        log_error("inference", "Error during YOLO inference on warmup image", e)

    roller_dict = {}  
    previous_od_state = False
    od_triggered = False
    roller_id_counter = 0  
    BIGFACE_DETECTED = False

    shared_data["od_inspected"] = 0
    shared_data["od_ok_rollers"] = 0
    shared_data["od_not_ok_rollers"] = 0
    shared_data["od_rust"] = 0
    shared_data["od_dent"] = 0
    shared_data["od_damage"] = 0
    shared_data["od_damage_on_end"] = 0
    shared_data["od_spherical_mark"] = 0
    shared_data["od_others"] = 0

    allow_all = shared_data.get("allow_all", False)
    if allow_all:
        allow_all_folder_od = f"C:\\Users\\{os.getlogin()}\\Desktop\\All Frames\\OD\\All_OD"
        os.makedirs(allow_all_folder_od, exist_ok=True)

    defect_thresholds = get_thresholds_for_model(model_od_path, 'od')
    model_conf_threshold = get_model_confidence_threshold(model_od_path, 'od')
    size_thresholds = get_size_thresholds_for_model(model_od_path, 'od')

    od_file_counter = 0
    od_all_file_counter = 0
    
    try:
        while True:
            current_od_state = shared_data["od_presence"]

            if current_od_state and not previous_od_state:
                od_triggered = True

                roller_id_counter += 1
                
                roller_dict[roller_id_counter] = {'defect': False , 'defect_names': ["No defect"]}
                log_info("inference", f"OD roller detected. Assigned Roller ID: {roller_id_counter}")
                print(f"\n🎯 OD New roller detected! Assigned Roller ID: {roller_id_counter}")

            if od_triggered:
                    
                with frame_lock_od:
                    np_frame = np.frombuffer(shared_frame_od.get_obj(), dtype=np.uint8).reshape(frame_shape)

                results = od_model.predict(np_frame, device=0, conf=model_conf_threshold, verbose=False, half=True, agnostic_nms=True)
                detections = []
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = float(box.conf[0])
                            class_id = int(box.cls[0])
                            label = od_model.names[class_id]
                            
                            detections.append((label, x1, y1, x2, y2, class_id, conf))

                filtered_detections = filter_detections(detections, defect_thresholds, size_thresholds)
                detections = sorted(filtered_detections, key=lambda x: x[1])
                annotated_frame = np_frame.copy()
                annotated_frame = annotate_detections(annotated_frame, filtered_detections)
            

                has_roller_detection = any(detection[0] == "roller" for detection in detections)
                has_defect_detection = any(detection[0] != "roller" for detection in detections)

                if allow_all and has_roller_detection:
                    od_all_file_counter += 1
                    allow_all_path = f"{allow_all_folder_od}/{od_all_file_counter}.jpg"
                    cv2.imwrite(allow_all_path, annotated_frame)
                if has_roller_detection and has_defect_detection:
                    od_file_counter += 1
                    save_path = f"{detected_folder}/{od_file_counter}.jpg"
                    cv2.imwrite(save_path, annotated_frame)

                with annotated_frame_lock_od:
                    np_annotated = np.frombuffer(shared_annotated_od.get_obj(), dtype=np.uint8).reshape(frame_shape)
                    np.copyto(np_annotated, annotated_frame)

                if len(detections) > 0:
                    roller_only_sorted = [detection for detection in detections if detection[0] == "roller" and detection[-1] > 0.80]
                    defect_only_sorted = [detection for detection in detections if detection[0] != "roller"]

                    for detection in defect_only_sorted:
                        
                        roller_id = point_inside( detection[1:5] , roller_only_sorted , roller_id_counter)

                        if roller_id == 0:
                            continue
                        
                        defect_detected =  False if roller_id == 0 else True

                        defect_name = "No Defect" if not defect_detected else od_model.names[detection[5]]

                        if roller_id in roller_dict:
                            roller_dict[roller_id]['defect'] |= defect_detected
                            roller_dict[roller_id]['defect_names'].append(defect_name)
                        else:
                            roller_dict[roller_id] = {'defect': defect_detected, 'defect_names': [defect_name]}

                if shared_data['bigface'] and not BIGFACE_DETECTED and len(roller_dict) > 0:
                    BIGFACE_DETECTED = True

                    defect_detected = list(roller_dict.values())[0]['defect']

                    first_key = next(iter(roller_dict))

                    if first_key in roller_dict:
                        if roller_updation_dict[first_key] == 0:
                            roller_data = roller_dict[first_key]
                            defect_detected = roller_data['defect']
                            defect_names = roller_data['defect_names']

                            if defect_detected:
                                log_info("inference", f"Defect detected for Roller ID: {first_key}")
                                shared_data["od_not_ok_rollers"] += 1
                            else:
                                log_info("inference", f"No defect for Roller ID: {first_key}")
                                shared_data["od_ok_rollers"] += 1

                            unique_defects = set(defect_names)

                            for defect_name in unique_defects:
                                defect_lower = defect_name.lower()
                                
                                if defect_lower == "rust":
                                    shared_data["od_rust"] += 1
                                elif defect_lower == "dent":
                                    shared_data["od_dent"] += 1
                                elif defect_lower == "damage":
                                    shared_data["od_damage"] += 1
                                elif defect_lower == "damage on end" or defect_lower == "damage_on_end":
                                    shared_data["od_damage_on_end"] += 1
                                elif defect_lower == "spherical mark" or defect_lower == "spherical_mark":
                                    shared_data["od_spherical_mark"] += 1
                                elif defect_lower != "no defect":
                                    shared_data["od_others"] += 1


                    roller_dict.pop(first_key) 
                    if roller_updation_dict[first_key] == 0 :
                        roller_queue_od.put(defect_detected)
                    del roller_updation_dict[first_key]
                
                elif not shared_data['bigface']:
                    BIGFACE_DETECTED = False

            previous_od_state = current_od_state
    except Exception as e:
        log_error("inference", "Error in OD roller processing", e)
        print(f"OD Roller Processing Error: {e}")
        shared_data["system_error"] = True

def handle_slot_control_od(roller_queue_od, shared_data, command_queue):
    """Control slot mechanism based on second proximity sensor."""
    set_priority_below_normal()
    
    if shared_data.get('debug_enabled', False):
        from frontend.utils.debug_logger import enable_debug
        enable_debug('inference')

    try:
        processing = False
        while True:
            if shared_data["od"] and not processing and not roller_queue_od.empty():
                processing = True
                if not roller_queue_od.empty():
                    defect_detected = roller_queue_od.get()
                    status = "❌ Defective" if defect_detected else "✅ Good"
                    command_queue.put(("reject_od" if defect_detected else "accept_od" , None))

                queue_size = roller_queue_od.qsize()

            elif not shared_data["od"]:
                processing = False
    except Exception as e:
        print(f"Slot Control Error: {e}")
        log_error("inference", "Error in slot control", e)
        shared_data["system_error"] = True    