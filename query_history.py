import json
from datetime import datetime
import os

class QueryHistory:
    def __init__(self, history_file='query_logs/history.json'):
        self.history_file = history_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        # Create directory if it doesn't exist
        directory = os.path.dirname(self.history_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create file if it doesn't exist
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def add_query(self, question, sql_query, status, results_count=0):
        """Save query to history"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question': question,
            'sql_query': sql_query,
            'status': status,
            'results_count': results_count
        }
        
        history.append(entry)
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_history(self, limit=10):
        """Retrieve recent queries"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        return history[-limit:][::-1]  # Most recent first
    
    def clear_history(self):
        """Clear all history"""
        with open(self.history_file, 'w') as f:
            json.dump([], f)