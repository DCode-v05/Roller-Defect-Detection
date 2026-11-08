"""
Process Manager Module
Handles proper cleanup of all processes and threads in the application
"""

import threading
import time
import psutil
import os
import gc
import torch
from typing import List, Optional


class ProcessManager:
    """Centralized process and thread management with proper cleanup."""
    
    def __init__(self):
        """Initialize process manager."""
        self.inference_processes = []
        self.inference_threads = []
        self.preview_processes = []
        self.preview_threads = []
        self.plc_process = None
        
    def register_inference_process(self, process):
        """Register an inference process for tracking."""
        if process and process not in self.inference_processes:
            self.inference_processes.append(process)
    
    def register_inference_thread(self, thread):
        """Register an inference thread for tracking."""
        if thread and thread not in self.inference_threads:
            self.inference_threads.append(thread)
    
    def register_preview_process(self, process):
        """Register a preview process for tracking."""
        if process and process not in self.preview_processes:
            self.preview_processes.append(process)
    
    def register_preview_thread(self, thread):
        """Register a preview thread for tracking."""
        if thread and thread not in self.preview_threads:
            self.preview_threads.append(thread)
    
    def register_plc_process(self, process):
        """Register PLC process for tracking."""
        self.plc_process = process
    
    def stop_inference_processes(self, timeout=5.0):
        """
        Stop all inference processes and their child processes.
        
        Args:
            timeout: Maximum time to wait for process termination
        """
        if self.plc_process and self.plc_process.is_alive():
            self._terminate_process_tree(self.plc_process, timeout)
            self.plc_process = None
        
        for process in self.inference_processes[:]:
            if process and process.is_alive():
                self._terminate_process_tree(process, timeout)
            self.inference_processes.remove(process)
    
    def stop_inference_threads(self, timeout=2.0):
        """
        Stop all inference threads gracefully.
        
        Args:
            timeout: Maximum time to wait for thread termination
        """
        for thread in self.inference_threads[:]:
            if thread and thread.is_alive():
                thread.join(timeout=timeout)
            self.inference_threads.remove(thread)
    
    def stop_preview_processes(self, timeout=5.0):
        """
        Stop all preview processes and their child processes.
        
        Args:
            timeout: Maximum time to wait for process termination
        """
        for process in self.preview_processes[:]:
            if process and process.is_alive():
                self._terminate_process_tree(process, timeout)
            self.preview_processes.remove(process)
    
    def stop_preview_threads(self, timeout=2.0):
        """
        Stop all preview threads gracefully.
        
        Args:
            timeout: Maximum time to wait for thread termination
        """
        for thread in self.preview_threads[:]:
            if thread and thread.is_alive():
                thread.join(timeout=timeout)
            self.preview_threads.remove(thread)
        
    
    def stop_all_inference(self):
        """Stop all inference-related processes and threads."""
        self.stop_inference_threads()
        self.stop_inference_processes()
    
    def stop_all_preview(self):
        """Stop all preview-related processes and threads."""
        self.stop_preview_threads()
        self.stop_preview_processes()
    
    def stop_everything(self):
        """Stop all processes and threads."""
        self.stop_all_inference()
        self.stop_all_preview()
    
    def _terminate_process_tree(self, parent_process, timeout=5.0):
        """
        Terminate a process and all its children.
        
        Args:
            parent_process: Parent process to terminate
            timeout: Maximum time to wait for termination
        """
        try:
            parent_pid = parent_process.pid
            
            try:
                parent = psutil.Process(parent_pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                gone, alive = psutil.wait_procs(children, timeout=timeout/2)
                
                for p in alive:
                    try:
                        p.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
            except psutil.NoSuchProcess:
                pass
            
            try:
                parent_process.terminate()
                parent_process.join(timeout=timeout/2)
                
                if parent_process.is_alive():
                    parent_process.kill()
                    parent_process.join(timeout=1.0)
                    
            except Exception as e:
                print(f"      ⚠️ Error terminating process: {e}")
                
        except Exception as e:
            print(f"   ⚠️ Error in process tree termination: {e}")
    
    def cleanup_gpu_memory(self):
        """Clean up GPU memory."""
        try:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception as e:
            print(f"⚠️ Error cleaning GPU memory: {e}")
    
    def get_status(self):
        """Get current status of all tracked processes and threads."""
        status = {
            'inference_processes': len([p for p in self.inference_processes if p.is_alive()]),
            'inference_threads': len([t for t in self.inference_threads if t.is_alive()]),
            'preview_processes': len([p for p in self.preview_processes if p.is_alive()]),
            'preview_threads': len([t for t in self.preview_threads if t.is_alive()]),
            'plc_process': self.plc_process.is_alive() if self.plc_process else False
        }
        return status


class ThreadStopFlag:
    """Thread-safe flag for signaling threads to stop."""
    
    def __init__(self):
        """Initialize stop flag."""
        self._stop_event = threading.Event()
    
    def set(self):
        """Set the stop flag."""
        self._stop_event.set()
    
    def clear(self):
        """Clear the stop flag."""
        self._stop_event.clear()
    
    def is_set(self):
        """Check if stop flag is set."""
        return self._stop_event.is_set()
    
    def wait(self, timeout=None):
        """Wait for stop flag to be set."""
        return self._stop_event.wait(timeout)
