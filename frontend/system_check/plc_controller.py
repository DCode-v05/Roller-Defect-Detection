"""
PLC Controller for System Check
Handles PLC communication and pattern-based roller control
"""

import snap7
from snap7.type import Areas
from snap7.util import set_bool, get_bool
import time
import threading


class PLCController:
    """PLC controller for System Check pattern-based control."""
    
    def __init__(self, app_instance, control_settings):
        """
        Initialize PLC controller.
        
        Args:
            app_instance: Reference to main WelVisionApp instance
            control_settings: Reference to ControlSettings component
        """
        self.app = app_instance
        self.control_settings = control_settings
        
        self.PLC_IP = "172.17.8.17"
        self.RACK = 0
        self.SLOT = 1
        self.DB_NUMBER = 86
        
        self.plc_client = None
        
        self.running = False
        self.monitoring_thread = None
        
        self.bf_counter = 0
        self.od_counter = 0
        
        self.bf_processed = 0
        self.bf_accepted = 0
        self.bf_rejected = 0
        
        self.od_processed = 0
        self.od_accepted = 0
        self.od_rejected = 0
        
        self.prev_bf_presence = False
        self.prev_od_presence = False
        self.prev_bf_accept_reject = False
        self.prev_od_accept_reject = False
    
    def connect(self):
        """Connect to PLC and set system ready bits."""
        try:
            self.plc_client = snap7.client.Client()
            self.plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
            
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            set_bool(data, byte_index=1, bool_index=6, value=True)
            set_bool(data, byte_index=1, bool_index=7, value=True)
            self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
            return True
        except Exception as e:
            print(f"❌ System Check: PLC Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PLC and reset system ready bits."""
        try:
            if self.plc_client:
                data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
                set_bool(data, byte_index=1, bool_index=6, value=False)
                set_bool(data, byte_index=1, bool_index=7, value=False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                
                self.plc_client.disconnect()
                self.plc_client = None
        except Exception as e:
            print(f"⚠ System Check: PLC Disconnect error: {e}")
            self.plc_client = None
    
    def start_monitoring(self):
        """Start PLC monitoring thread."""
        if self.running:
            print("⚠ System Check: Monitoring already running")
            return False
        
        if not self.connect():
            return False
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        return True
    
    def stop_monitoring(self):
        """Stop PLC monitoring thread."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        self.disconnect()
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in separate thread."""
        while self.running:
            try:
                if not self.plc_client:
                    print("⚠ System Check: PLC client disconnected, stopping monitor loop")
                    if hasattr(self.app, 'shared_data') and self.app.shared_data:
                        self.app.shared_data['system_error'] = True
                    break
                
                data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 3)
                
                bf_presence = get_bool(data, 0, 1)
                
                od_presence = get_bool(data, 1, 4)
                
                bf_accept_reject = get_bool(data, 0, 2)
                
                od_accept_reject = get_bool(data, 0, 0)
                
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['bigface_presence'] = bf_presence
                    self.app.shared_data['od_presence'] = od_presence
                    self.app.shared_data['bigface'] = bf_accept_reject
                    self.app.shared_data['od'] = od_accept_reject
                
                if bf_presence and not self.prev_bf_presence:
                    self._handle_bf_presence()
                
                if od_presence and not self.prev_od_presence:
                    self._handle_od_presence()
                
                if bf_accept_reject and not self.prev_bf_accept_reject:
                    self._handle_bf_accept_reject()
                
                if od_accept_reject and not self.prev_od_accept_reject:
                    self._handle_od_accept_reject()
                
                self.prev_bf_presence = bf_presence
                self.prev_od_presence = od_presence
                self.prev_bf_accept_reject = bf_accept_reject
                self.prev_od_accept_reject = od_accept_reject
                
            except Exception as e:
                if self.running:
                    print(f"❌ System Check: Monitoring error: {e}")
                    if hasattr(self.app, 'shared_data') and self.app.shared_data:
                        self.app.shared_data['system_error'] = True
                    time.sleep(0.1)
                else:
                    break
    
    def _handle_bf_presence(self):
        """Handle BigFace roller presence detection - increment processed counter."""
        self.bf_processed += 1
        
        self._update_statistics()
        
    
    def _handle_od_presence(self):
        """Handle OD roller presence detection - increment processed counter."""
        self.od_processed += 1
        
        self._update_statistics()
        
    
    def _handle_bf_accept_reject(self):
        """Handle BigFace accept/reject trigger - send signal and update counters."""
        bf_pattern = self.control_settings.bf_pattern
        
        if bf_pattern == "ACCEPT ALL":
            accept = True
        elif bf_pattern == "REJECT ALL":
            accept = False
        else:
            accept = (self.bf_counter % 2 == 0)
            self.bf_counter += 1
        
        if accept:
            self.bf_accepted += 1
        else:
            self.bf_rejected += 1
        
        self._send_bf_signal(accept)
        
        self._update_statistics()
        
        status = "ACCEPTED" if accept else "REJECTED"
    
    def _handle_od_accept_reject(self):
        """Handle OD accept/reject trigger - send signal and update counters."""
        od_pattern = self.control_settings.od_pattern
        
        if od_pattern == "ACCEPT ALL":
            accept = True
        elif od_pattern == "REJECT ALL":
            accept = False
        else:
            accept = (self.od_counter % 2 == 0)
            self.od_counter += 1
        
        if accept:
            self.od_accepted += 1
        else:
            self.od_rejected += 1
        
        self._send_od_signal(accept)
        
        self._update_statistics()
        
        status = "ACCEPTED" if accept else "REJECTED"
    
    def _send_bf_signal(self, accept):
        """
        Send accept/reject signal to PLC for BigFace.
        
        Args:
            accept: True to accept, False to reject
        """
        try:
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            
            if accept:
                set_bool(data, 1, 0, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 0, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            else:
                set_bool(data, 1, 1, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 1, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
        except Exception as e:
            print(f"⚠ System Check: Error sending BF signal: {e}")
            if hasattr(self.app, 'shared_data') and self.app.shared_data:
                self.app.shared_data['system_error'] = True
    
    def _send_od_signal(self, accept):
        """
        Send accept/reject signal to PLC for OD.
        
        Args:
            accept: True to accept, False to reject
        """
        try:
            data = self.plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
            
            if accept:
                set_bool(data, 1, 2, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 2, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            else:
                set_bool(data, 1, 3, True)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                time.sleep(0.1)
                set_bool(data, 1, 3, False)
                self.plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
            
        except Exception as e:
            print(f"⚠ System Check: Error sending OD signal: {e}")
            if hasattr(self.app, 'shared_data') and self.app.shared_data:
                self.app.shared_data['system_error'] = True
    
    def _update_statistics(self):
        """Update shared data statistics for UI display."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            self.app.shared_data['system_check_bf_processed'] = self.bf_processed
            self.app.shared_data['system_check_bf_accepted'] = self.bf_accepted
            self.app.shared_data['system_check_bf_rejected'] = self.bf_rejected
            
            self.app.shared_data['system_check_od_processed'] = self.od_processed
            self.app.shared_data['system_check_od_accepted'] = self.od_accepted
            self.app.shared_data['system_check_od_rejected'] = self.od_rejected
            
            total_passed = self.bf_processed
            
            total_accepted = self.od_accepted
            
            total_rejected = self.bf_rejected + self.od_rejected
            
            self.app.shared_data['system_check_total_passed'] = total_passed
            self.app.shared_data['system_check_total_accepted'] = total_accepted
            self.app.shared_data['system_check_total_rejected'] = total_rejected
    
    def reset_counters(self):
        """Reset all processing counters."""
        self.bf_processed = 0
        self.bf_accepted = 0
        self.bf_rejected = 0
        
        self.od_processed = 0
        self.od_accepted = 0
        self.od_rejected = 0
        
        self.bf_counter = 0
        self.od_counter = 0
        
        self._update_statistics()
